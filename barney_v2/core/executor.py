"""
Executor: Carries out the strategic plan using tools.
Refined for robust JSON parsing and step execution.
"""

import os
import json
import re
import importlib
from core.llm import call_llm
from core.scoring import calculate_depth_score, get_required_depth
from core.tools import TOOLS


# Global Plan Cache for Stress Test Stability (Step #3)
_plan_cache = {}


def _clean_json(text: str) -> str:
    """Robust JSON extraction from LLM response."""
    # Find the outermost { ... }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1:
        return text[first_brace:last_brace+1]
    return text.strip()


def _get_tool(tool_name: str):
    """Dynamically load tool by name."""
    try:
        module = importlib.import_module(f"tools.{tool_name}")
        return getattr(module, tool_name)
    except (ImportError, AttributeError):
        return None


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


def _call_tool(tool_name, input_data):
    """Action-Capable Dispatcher (Step #3)."""
    tool = TOOLS.get(tool_name)
    if not tool:
        return f"Error: Tool '{tool_name}' not found in registry."
    return tool(input_data)


def enforce_structure(strategy, answer):
    """Surgical Structure Enforcement: Density + Intent (Final Fix #1)."""
    text = answer.lower()

    if strategy == "compare":
        # Density check: needs criteria AND multiple 'vs'/'|' AND a conclusion
        return (
            ("criteria" in text or "based on" in text) and
            (text.count("vs") >= 1 or "|" in answer) and
            ("better" in text or "overall" in text or "therefore" in text)
        )

    if strategy == "rank":
        # Density check: needs multiple numbers AND multiple justifications
        return (
            sum(1 for i in range(1, 5) if str(i) in text) >= 2 and
            text.count("because") >= 2
        )

    if strategy == "validate":
        return (
            "because" in text and
            ("therefore" in text or "this means" in text)
        )

    return True


def execute(task: str, memory_context: str = "", strategy: str = "explore", 
            strategy_warning: str = "", suggested_strategy: str = None, 
            confidence: float = 0.0, avg_steps: float = 0.0,
            mode: str = "real", forced_outcome: dict = None,
            reason_traces: list = None) -> dict:
    """
    Execute task with Strategy-Guided Planning.
    """
    # 1. Plan Phase
    if mode == "deterministic" and task in _plan_cache:
        plan_data = _plan_cache[task]
        plan = plan_data.get("steps", [])
    else:
        bhv_rules = ""
        if suggested_strategy == "validate":
            bhv_rules = "\n- Use 'validate' rules: verify every premise, check cross-references, summarize confidence."
        elif suggested_strategy == "compare":
            bhv_rules = "\n- Use 'compare' rules: search at least 2 entities, list pros/cons, provide final verdict."
        elif suggested_strategy == "rank":
            bhv_rules = "\n- Use 'rank' rules: search multiple options, apply criteria, output numbered list."

        strategy_injection = (
            f"\n\nStrategy: {suggested_strategy.upper() if suggested_strategy else 'EXPLORE'} (conf: {confidence:.2f}, avg: {avg_steps:.1f})\n\n"
            f"Please structure your reasoning using {suggested_strategy if suggested_strategy else 'exploration'}.\n"
            f"STRATEGY BEHAVIOR:{bhv_rules}\n"
            f"- Prefer fewer steps and minimal tool usage, BUT your primary goal is to produce a USEFUL and MEANINGFUL result.\n"
            f"- Avoid shallow, generic, or incomplete answers. Provide reasons (use 'because') or structured examples.\n"
            f"- Output MUST be a valid JSON object starting with {{ and ending with }}.\n"
        )

        # --- REASONING TRACE INJECTION (Phase #4A) ---
        trace_injection = ""
        if reason_traces:
            # Format: search -> compare -> validate
            formatted_traces = [" → ".join(t) for t in reason_traces]
            trace_injection = (
                "\n\nSuccessful reasoning patterns (similar tasks):\n"
                "- " + "\n- ".join(formatted_traces) + "\n"
                "Use this as guidance if applicable. Do NOT force it if irrelevant.\n"
            )
            print(f"  🧠 [reasoning] Injected traces: {', '.join(formatted_traces)}")

        sys_prompt = (
            "You are Barney v2, a task-planning AI.\n"
            "Generate a multi-step strategic plan to solve the task.\n\n"
            "Format: {\"type\": \"plan\", \"steps\": [\"step 1\", \"step 2\"]}"
            f"{strategy_injection}"
            f"{trace_injection}"
        )
        
        user_prompt = f"Task: {task}\nPrior Context: {memory_context}"
        
        try:
            plan_response = call_llm(user_prompt, system_prompt=sys_prompt)
            clean_p = _clean_json(plan_response)
            plan_data = json.loads(clean_p, strict=False)
            plan = plan_data.get("steps", [])
            _plan_cache[task] = plan_data
            
            # --- SEMANTIC VALIDATION (NEW) ---
            # Reject lazy/generic 1-step plans for structured tasks
            is_structured = suggested_strategy in ["compare", "rank", "validate"]
            generic_words = ["analyze", "search", "summarize", "evaluate"]
            is_generic = all(any(gw in s.lower() for gw in generic_words) for s in plan) and len(plan) < 3
            
            if is_structured and (len(plan) < 3 or is_generic):
                print(f"  ⚠️ [validator] Generic/Shallow plan detected for '{suggested_strategy}'. Forcing depth.")
                if suggested_strategy == "compare":
                    plan = [
                        "Analyze the core entities and identify 5 key criteria for comparison.",
                        "Gather detailed strengths, weaknesses, and specs for EACH entity.",
                        "Create a point-by-point comparative breakdown (Pros/Cons).",
                        "Synthesize findings into a final definitive recommendation."
                    ]
                elif suggested_strategy == "rank":
                    plan = [
                        "Identify the top candidates based on the task parameters.",
                        "Evaluate each candidate against specific performance/cost metrics.",
                        "Assign relative rankings with explicit 'because' justifications.",
                        "Produce the final ranked list with a 'Top Pick' breakdown."
                    ]
                else: # validate
                    plan = [
                        "Identify the primary claim or information to be verified.",
                        "Cross-reference the claim against multiple diverse sources or logic paths.",
                        "Assess the credibility and confidence level of the findings.",
                        "State the final verification status with supporting evidence."
                    ]
        except Exception as e:
            print(f"  📋 [planner] Warning: Plan parsing failed. Falling back. ({e})")
            plan = [f"Provide a detailed response to the task: {task}"]

    # 2. DETERMINISTIC OVERRIDE
    if mode == "deterministic" and forced_outcome:
        return {
            "task": task,
            "result": forced_outcome.get("final_answer", "Forced Result"),
            "plan": plan,
            "steps": forced_outcome.get("steps", len(plan)),
            "tool_calls": forced_outcome.get("tool_calls", 0),
            "success": forced_outcome.get("success", True),
            "outcome_score": forced_outcome.get("outcome_score", 1),
            "cost": {"steps": forced_outcome.get("steps", len(plan)), "tool_calls": forced_outcome.get("tool_calls", 0)}
        }

    # 3. Real Execution Phase
    steps_taken = []
    tool_calls_count = 0
    tool_call_history = [] # For exact redundancy check (Fix #3)
    has_repeated_tool = False
    current_context = f"History of successful poisoning/failures: {memory_context}"

    for i, step in enumerate(plan):
        print(f"  🔧 [executor] Step {i+1}: {step}")
        
        # --- REGENERATION LOOP (Step #4) ---
        MAX_RETRIES = 2
        final_step_answer = None
        
        for attempt in range(1, MAX_RETRIES + 2):
            retry_instruction = ""
            if attempt == 2:
                retry_instruction = "\n\n⚠️ REJECTION: Your previous answer was shallow. Add reasoning, examples, and technical evidence."
            elif attempt == 3:
                retry_instruction = "\n\n🚨 CRITICAL: Your answer lacked reasoning and examples. You MUST include concrete details, tools, or comparisons. DO NOT BE GENERIC."

            step_prompt = (
                f"Current Task: {task}\n"
                f"Current Goal (Step {i+1}): {step}\n"
                f"History Context (Grounded): {current_context}\n\n"
                "Respond with a STRICT JSON object:\n"
                "{\n"
                "  \"action\": \"tool\" | \"final\",\n"
                "  \"tool\": \"search\" | \"python\",\n"
                "  \"input\": \"query or code\",\n"
                "  \"answer\": \"your final response if action=final\"\n"
                "}\n\n"
                "Tools Available:\n"
                "- search: Use for real-world facts (DuckDuckGo).\n"
                "- python: Use for complex math or computation (No imports).\n\n"
                "Rules (Tool Discipline):\n"
                "- Use tools ONLY when needed. Ground your reasoning in reality.\n"
                "- Do NOT call the same tool repeatedly with similar input.\n"
                "- Every 'final' answer MUST include a reason ('because') and concrete details/examples.\n"
                "- Avoid generic statements like 'it depends'.\n"
                f"{retry_instruction}"
            )
            
            try:
                resp = call_llm(step_prompt, system_prompt="Focus on building a high-value, grounded response.")
                action_data = parse_tool_call(resp)
                
                if not action_data or "action" not in action_data:
                    print(f"  📋 [parser] Failed to parse tool call. Treating as final_answer fallback.")
                    # Baseline quality fallback: assume the text itself is useful? 
                    # No, let's treat as shallow failure so it retries.
                    continue
                
                action = action_data["action"]
                
                if action == "tool":
                    tool_name = action_data.get("tool")
                    tool_input = action_data.get("input")
                    
                    # --- REDUNDANCY DETECTION (Fix #3) ---
                    call_signature = (tool_name, tool_input)
                    if call_signature in tool_call_history:
                        has_repeated_tool = True
                        print(f"  ⚠️ [tool_misuse] Detected repeated call: {tool_name}(\"{tool_input[:30]}...\")")
                    
                    tool_call_history.append(call_signature)
                    tool_calls_count += 1
                    print(f"  🔧 [tool] {tool_name}(\"{tool_input[:50]}...\")")
                    
                    result_raw = _call_tool(tool_name, tool_input)
                    # --- CONTEXT-AWARE APPENDING (Fix #5) ---
                    current_context += f"\n[Step {i+1}] Tool:{tool_name} Result: {result_raw}"
                    # Tools don't need depth check, but they do move us to next step or next attempt
                    break 
                    
                elif action == "final":
                    answer = action_data.get("answer", "")
                    if not answer: answer = action_data.get("input", "") # Fallback common mistakes
                    
                    # --- EXECUTION QUALITY CHECK ---
                    depth = calculate_depth_score(answer)
                    req_depth = get_required_depth(task)
                    structure_ok = enforce_structure(suggested_strategy, answer)
                    
                    print(f"  📊 [validator] Attempt {attempt}: depth={depth}/{req_depth}, structure={'OK' if structure_ok else 'FAIL'}")
                    
                    if (depth >= req_depth and structure_ok) or attempt == MAX_RETRIES + 1:
                        final_step_answer = answer
                        break
                    else:
                        print(f"  🔄 [retry] Rejecting answer. Escalating pressure.")
                        continue
                        
            except Exception as e:
                print(f"  🔧 [executor] Warning: Step failed ({e}). Attempting next.")
                break
        
        if final_step_answer:
            return {
                "task": task, "result": final_step_answer, "plan": plan, 
                "steps": i + 1, "tool_calls": tool_calls_count,
                "repeated_tool": has_repeated_tool,
                "cost": {"steps": i + 1, "tool_calls": tool_calls_count}
            }

    return {
        "task": task, "result": current_context, "plan": plan, 
        "steps": len(plan), "tool_calls": tool_calls_count,
        "repeated_tool": has_repeated_tool,
        "cost": {"steps": len(plan), "tool_calls": tool_calls_count}
    }
