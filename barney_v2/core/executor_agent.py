"""
Executor Agent: The Tactical Hand. 
Decides HOW to do it (Tools, Depth, Action).
Strictly follows the Planner's steps.
"""

import json
import hashlib
from core.llm import call_llm
from core.tools import TOOLS
from core.scoring import calculate_depth_score, get_required_depth
from redis_client import append_log, get_tool_result, save_tool_result

def parse_tool_call(output: str):
    """Robust JSON extraction for Tool Selection (Fix #2)."""
    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        if start == -1 or end == 0: return None
        json_str = output[start:end]
        return json.loads(json_str, strict=False)
    except:
        return None

def _call_tool(tool_name, input_data, task_id=None, replan_counter=0, step_id=None, step_idx=0):
    """Action-Capable Dispatcher with Granular Tool Idempotency (Phase 37b)."""
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found in registry."
    
    NON_IDEMPOTENT_TOOLS = ["get_time", "random", "live_search"]
    
    # 1. Generate Idempotency Key (Deterministic sorted JSON + MD5)
    try:
        serialized_args = json.dumps(input_data, sort_keys=True)
    except:
        serialized_args = str(input_data) # Fallback for non-serializable
        
    args_hash = hashlib.md5(serialized_args.encode()).hexdigest()[:12]
    # Correct Key Structure: Includes tool_name to avoid collisions
    idempotency_key = f"{task_id}:{replan_counter}:{step_id}:{tool_name}:{args_hash}"
    
    # 2. Cache Bypass Check
    if tool_name in NON_IDEMPOTENT_TOOLS:
        print(f"  ⏭️ [tool-idempotency] SKIP tool={tool_name} (Non-idempotent)")
    elif task_id and step_id:
        # 3. Cache Hit Check
        cached = get_tool_result(idempotency_key)
        if cached is not None:
            print(f"  🎯 [tool-idempotency] HIT tool={tool_name} step={step_idx+1}")
            if task_id:
                append_log(task_id, f"🎯 [tool-idempotency] Cache HIT for {tool_name}")
            return cached

    # 4. Execution
    if task_id:
        append_log(task_id, f"🔧 [TOOL] {tool_name} called with: {str(input_data)[:200]}...")

    tool = TOOLS.get(tool_name)
    result = tool(input_data)
    
    # 5. Result Validation & Persistence
    if task_id and step_id and tool_name not in NON_IDEMPOTENT_TOOLS and result:
        # Simple poison-proof check: must be non-empty and non-failed
        is_valid = True
        result_str = str(result).lower()
        if "error" in result_str or "failed" in result_str or "exception" in result_str:
            is_valid = False
            
        if is_valid:
            try:
                serialized_res = json.dumps(result)
                if len(serialized_res) < 20000: # 20KB Size Guard
                    save_tool_result(idempotency_key, result)
                    print(f"  💾 [tool-idempotency] STORE tool={tool_name} size={len(serialized_res)/1024:.1f}KB")
                else:
                    print(f"  ⚠️ [tool-idempotency] OVERSIZE tool={tool_name} ({len(serialized_res)/1024:.1f}KB). Skipping cache.")
            except:
                print(f"  ⚠️ [tool-idempotency] SERIALIZATION_FAIL for {tool_name}. Skipping cache.")

    if task_id:
        append_log(task_id, f"✅ [TOOL RESULT] {str(result)[:200]}...")
        
    return result

def enforce_structure(strategy, answer):
    """Surgical Structure Enforcement: Density + Intent (Final Fix #1)."""
    text = answer.lower()
    if strategy == "compare":
        return (("criteria" in text or "based on" in text) and (text.count("vs") >= 1 or "|" in answer))
    if strategy == "rank":
        return (sum(1 for i in range(1, 4) if str(i) in text) >= 2)
    if strategy == "validate":
        return ("because" in text)
    return True

def validate_plan_execution(plan: dict, executed_steps: list) -> tuple:
    """Mechanical Plan Validation (User Requirement Step #1)."""
    if not executed_steps:
        return False, "No steps executed"
    if len(executed_steps) < len(plan.get("steps", [])):
        return False, f"Skipped steps: executed {len(executed_steps)} of {len(plan['steps'])}"
    
    # Check if all steps were attempted (basic string alignment)
    for i, step in enumerate(plan.get("steps", [])):
        if i >= len(executed_steps):
            return False, f"Step mismatch at index {i}"
            
    return True, "OK"

def execute_single_step(task: str, step: str, step_idx: int, total_steps: int, 
                        history: str = "", tool_history: list = None, constraints: dict = None,
                        strategy_type: str = "explore", task_id: str = None, role: str = "fast",
                        replan_counter: int = 0, step_id: str = None) -> dict:
    """Tactical Execution of exactly one plan item (Phase 35)."""
    remaining_steps = total_steps - step_idx
    if tool_history is None: tool_history = []
    
    current_context = history
    MAX_RETRIES = 2
    final_output = None
    tool_calls_this_step = 0
    repeated_detected = False

    for attempt in range(1, MAX_RETRIES + 2):
        retry_instruction = ""
        if attempt > 1:
            retry_instruction = "\n\n⚠️ REJECTION: Your previous response was shallow. Add evidence and technical details."

        step_prompt = (
            f"Task: {task}\n"
            f"Planned Step {step_idx+1}: {step}\n"
            f"Current Step: {step_idx+1} of {total_steps}\n"
            f"Successful History: {current_context}\n\n"
            "You are the EXECUTOR. You MUST follow the provided plan strictly.\n"
            "Output STRICT JSON:\n"
            "{\n"
            "  \"action\": \"tool\" | \"final\",\n"
            "  \"justification\": {\n"
            "    \"intent\": \"Why this step is needed\",\n"
            "    \"expected_outcome\": \"What should happen (Specific/Measurable)\",\n"
            "    \"risk_reason\": \"Why this risk is acceptable\",\n"
            "    \"alternatives\": [\"Other possible approaches\"]\n"
            "  },\n"
            "  \"tool\": \"search\" | \"python\" | \"http_fetch\" | \"get_time\" | \"list_dir\" | \"read_file\" | \"write_file\",\n"
            "  \"input\": \"JSON dictionary e.g., {'code': '...'} or {'url': '...'} or {'query': '...'}\",\n"
            "  \"answer\": \"your final response if action=final\"\n"
            "}\n\n"
            "Tactical Rules:\n"
            "- FILESYSTEM: ALWAYS provide JSON for write_file: {\"filename\": \"secret.txt\", \"content\": \"data\"}.\n"
            "- TOOL PRIORITY: Use 'write_file' for saving data. NEVER use 'python' for 'os.' or 'open()'.\n"
            "- PROGRESSION: Your tool input MUST be unique and more specific than previous steps.\n"
            "- NO REPETITION: Do NOT use exactly same search/file inputs as previous steps in 'History'.\n"
            "- EVIDENCE: If using a tool, refine the query to target missing details.\n"
            "- CONSTRAINTS: Must satisfy: " + str(constraints) + "\n"
            "- FINALITY: If step is 'Final' or 'Synthesize', include reasoning ('because') and data.\n"
            f"{retry_instruction}"
        )

        try:
            resp_data = call_llm(step_prompt, system_prompt="Focus on building an efficient, grounded, and PROGRESSIVE response.", role=role, task_id=task_id, remaining_steps=remaining_steps)
            
            # Phase 12.5: Terminal Brain Failure awareness
            if isinstance(resp_data, dict) and resp_data.get("status") == "LLM_FAILURE":
                 print(f"    🚨 [executor] Tactical Brain Failure: {resp_data.get('error')}")
                 return {"status": "failed", "reason": "BRAIN_DEAD", "error": resp_data.get("error")}

            resp_text = resp_data.get("content", "")
            action_data = parse_tool_call(resp_text)
            if not action_data:
                print(f"    ⚠️ [executor] Parsing Failed. Attempt {attempt}/{MAX_RETRIES+1}")
                continue

            action = action_data.get("action")
            if action == "tool":
                tool_name = action_data.get("tool")
                tool_input = action_data.get("input")
                
                # Progressive Query Enforcement (Phase 9: Handle Dict inputs)
                input_str = json.dumps(tool_input) if isinstance(tool_input, dict) else str(tool_input)
                is_redundant = any((json.dumps(t[1]) if isinstance(t[1], dict) else str(t[1])).lower().strip() == input_str.lower().strip() for t in tool_history)
                
                if is_redundant:
                    print(f"    ⚠️ [executor] Redundant input rejected: '{input_str[:30]}...'")
                    current_context += f"\n[Step {step_idx+1}] Error: Your tool input was redundant. Please try a more specific query."
                    repeated_detected = True
                    continue 

                tool_history.append((tool_name, tool_input))
                tool_calls_this_step += 1
                
                print(f"    🔧 [tool] {tool_name}(\"{input_str[:30]}...\")")
                # Phase 37b: Propagate context for tool idempotency
                # We need step_id here. execute_single_step should probably receive it or generate it.
                # In core/loop.py, we already generate step_id. 
                # For execute_single_step to be stateless-aware, we add step_id to its args.
                result_raw = _call_tool(tool_name, tool_input, task_id=task_id, replan_counter=replan_counter, step_id=step_id, step_idx=step_idx)
                current_context += f"\n[Step {step_idx+1}] Tool:{tool_name} Result: {result_raw}"
                # Successful tool call -> finish step
                return {
                    "status": "success", "executed_step": step, 
                    "history_update": current_context, "tool_calls": tool_calls_this_step,
                    "repeated_tool": repeated_detected, "answer": None,
                    "model": resp_data.get("model"), "confidence": resp_data.get("confidence")
                }

            elif action == "final":
                answer = action_data.get("answer", "")
                depth = calculate_depth_score(answer)
                req_depth = get_required_depth(task)
                struct_ok = enforce_structure(strategy_type, answer)
                
                if (depth >= req_depth and struct_ok) or attempt == MAX_RETRIES + 1:
                    return {
                        "status": "success", "executed_step": step, 
                        "history_update": current_context + f"\n[Final Output]: {answer}",
                        "tool_calls": tool_calls_this_step, 
                        "repeated_tool": repeated_detected, "answer": answer,
                        "model": resp_data.get("model"), "confidence": resp_data.get("confidence")
                    }
                else: continue
        except Exception as e:
            print(f"    🚨 [executor] Tactical error in Step {step_idx+1}: {e}")
            continue
            
    return {"status": "failed", "reason": "Max retries hit for single step execution."}

def execute_plan(task: str, plan_data: dict, memory_context: str = "", task_id: str = None, replan_counter: int = 0) -> dict:
    """Legacy compatibility: Execute whole plan at once."""
    steps = plan_data.get("steps", [])
    constraints = plan_data.get("constraints", {})
    strategy_type = plan_data.get("strategy", "explore")

    executed_steps = []
    tool_history = []
    tool_calls_count = 0
    has_repeated_tool = False
    current_context = f"History: {memory_context}"
    final_output = None

    for i, step in enumerate(steps):
        print(f"  ⚙️ [executor] Step {i+1}/{len(steps)}: {step}")
        res = execute_single_step(task, step, i, len(steps), current_context, tool_history, constraints, strategy_type, task_id=task_id)
        
        if res["status"] == "success":
            executed_steps.append(step)
            current_context = res["history_update"]
            tool_calls_count += res["tool_calls"]
            if res["repeated_tool"]: has_repeated_tool = True
            if res["answer"]: final_output = res["answer"]
        else:
            # Plan execution failed
            break

    # Final Validation
    is_valid, validation_reason = validate_plan_execution(plan_data, executed_steps)
    if not is_valid:
        print(f"  🚨 [executor] Plan execution validation failed: {validation_reason}")
        return {
            "status": "failed", "reason": validation_reason,
            "context": {
                "failed_step": i, "reason": validation_reason,
                "executed_steps": executed_steps, "tool_history": tool_history,
                "previous_strategy": strategy_type
            }
        }

    return {
        "status": "success", "result": final_output or current_context,
        "tool_calls": tool_calls_count, "repeated_tool": has_repeated_tool,
        "steps_count": len(executed_steps), "executed_steps": executed_steps
    }
