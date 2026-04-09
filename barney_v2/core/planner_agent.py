import json
from core.llm import call_llm
from core.memory_manager import retrieve_similar, detect_task_reuse

def _clean_json(text: str) -> str:
    """Robust JSON extraction from LLM response."""
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1:
        return text[first_brace:last_brace+1]
    return text.strip()

def generate_plan(task: str, memory_context: str = "", strategy_info: dict = None, reason_traces: list = None, task_id: str = None) -> dict:
    """Initial Strategic Planning with Tool Affinity and Semantic Memory (Phase 12)."""
    suggested_strategy = strategy_info.get("suggested_strategy")
    confidence = strategy_info.get("confidence", 0.0)
    avg_steps = strategy_info.get("avg_steps", 0.0)
    
    # 🧠 Phase 12: Semantic Memory Retrieval
    # Inject Top-K similar + 1 Random Low-Confidence Diversity Outlier
    ledger_insights = retrieve_similar(task, top_k=3)
    memory_injection = ""
    if ledger_insights:
        memory_injection = "\n--- RELEVANT INSIGHTS (HYBRID WEIGHTED) ---\n"
        for i, entry in enumerate(ledger_insights):
            memory_injection += f"{i+1}. {entry['summary']} (Weight: {entry['effective_weight']:.2f})\n"
        memory_injection += "-------------------------------------------\n"
    
    # Update memory_context with ledger insights
    combined_context = memory_context + memory_injection
    
    # 📝 Tool Affinity Injection (Phase 7 Fix)
    from core.insight_engine import get_task_type
    task_type = get_task_type(task)
    tool_guidance = ""
    if task_type == "compute":
        tool_guidance = "\n- TASK TYPE: COMPUTE. Suggest using 'python' tool specifically for logic and calculation."
    elif task_type == "web":
        tool_guidance = "\n- TASK TYPE: WEB. Use 'search' for latest info."

    bhv_rules = ""
    if suggested_strategy == "validate":
        bhv_rules = "\n- Use 'validate' rules: verify every premise, check cross-references, summarize confidence."
    elif suggested_strategy == "compare":
        bhv_rules = "\n- Use 'compare' rules: search at least 2 entities, list pros/cons, provide final verdict."
    elif suggested_strategy == "rank":
        bhv_rules = "\n- Use 'rank' rules: search multiple options, apply criteria, output numbered list."

    strategy_injection = (
        f"\n\nStrategy: {suggested_strategy.upper() if suggested_strategy else 'EXPLORE'} (conf: {confidence:.2f}, avg: {avg_steps:.1f})\n"
        f"STRATEGY BEHAVIOR:{bhv_rules}\n"
        f"{tool_guidance}"
    )

    trace_injection = ""
    if reason_traces:
        formatted_traces = [" → ".join(t) for t in reason_traces]
        trace_injection = (
            "\nSuccessful reasoning patterns (similar tasks):\n"
            "- " + "\n- ".join(formatted_traces) + "\n"
        )

    sys_prompt = (
        "You are the Planner Agent for Barney v2.\n"
        "Your goal is to define the strategic WHAT of a task. Do NOT execute it.\n\n"
        "Output MUST be a strict JSON object:\n"
        "{\n"
        "  \"status\": \"OK\" | \"INSUFFICIENT_CONFIDENCE\",\n"
        "  \"reason\": \"Explain why confidence is low (if applicable)\",\n"
        "  \"strategy\": \"compare\" | \"rank\" | \"validate\" | \"explore\",\n"
        "  \"constraints\": {\n"
        "    \"min_steps\": int,\n"
        "    \"require_evidence\": bool,\n"
        "    \"structure\": \"string\"\n"
        "  },\n"
        "  \"steps\": [\"step 1\", \"step 2\", ...]\n"
        "}\n\n"
        "Rules:\n"
        "- [MEMORY TRUST]: If weight < 0.4, treat memory as UNVERIFIED. If weight > 0.8, favor reuse.\n"
        "- [HONESTY]: If ambiguity > 0.7 or sources are inconsistent/weak, do NOT fabricate a plan. Return 'INSUFFICIENT_CONFIDENCE'.\n"
        "- Minimum 3 steps for structured tasks.\n"
        "- Steps should be actionable but high-level.\n"
        "- [PERSISTENCE DISCIPLINE]: Avoid speculative file creation. However, if a task explicitly requests saving data (e.g., 'save to', 'write file'), you MUST include a 'write_file' step.\n"
        f"{strategy_injection}"
        f"{trace_injection}"
    )

    user_prompt = f"Task: {task}\nPriorContext: {combined_context}"
    
    print(f"  🧠 [planner] Generating plan for: {task[:50]}...")
    try:
        print(f"  🧠 [planner] Sending request to LLM (Role: Strong)...")
        resp_data = call_llm(user_prompt, system_prompt=sys_prompt, role="strong", task_id=task_id)
        
        # Phase 12.5: Handle Structured Error Dicts
        if isinstance(resp_data, dict) and resp_data.get("status") == "LLM_FAILURE":
             print(f"  🚨 [planner] Terminal Brain Failure: {resp_data.get('error')}")
             return {"status": "FAILED", "reason": "BRAIN_DEAD", "error": resp_data.get("error")}

        resp_text = resp_data.get("content", "")
        print(f"  🧠 [planner] Received LLM response (len={len(resp_text)}) | Confidence: {resp_data.get('confidence')}")
        plan_data = json.loads(_clean_json(resp_text), strict=False)
        
        # Semantic Validation: Ensure structured tasks have depth
        is_structured = suggested_strategy in ["compare", "rank", "validate"]
        steps = plan_data.get("steps", [])
        
        # Guard: Convert all steps to strings
        plan_data["steps"] = [str(s) for s in steps]
        steps = plan_data["steps"]

        if is_structured and len(steps) < 3:
            # Injecting default deep plan if LLM is lazy
            plan_data["steps"] = [
                f"Analyze core entities for {task}",
                "Gather grounded evidence and specs via tools",
                "Apply criteria and generate structured breakdown",
                "Synthesize final verdict with reasoning"
            ]
            plan_data["constraints"]["min_steps"] = 4
            
        return plan_data
    except Exception as e:
        print(f"  🧠 [planner] Warning: Initial plan failed ({e}). Falling back.")
        return {
            "strategy": suggested_strategy or "explore",
            "constraints": {"min_steps": 1, "require_evidence": False},
            "steps": [f"Solve task: {task}"]
        }

def prune_constraints(constraints: dict, limit: int = 5) -> dict:
    """
    Prevents 'Planner Fatigue' by limiting active constraints.
    Prioritizes HARD constraints and the most recent ones.
    """
    if len(constraints) <= limit:
        return constraints
    
    # Simple priority: HARD first, then latest
    # Since we use dict, we'll convert to list to sort
    items = list(constraints.items())
    # Sort: [HARD CONSTRAINT] starts with "["
    items.sort(key=lambda x: 0 if "[HARD" in str(x[1]) else 1)
    
    return dict(items[:limit])

def replan(task: str, feedback: dict, memory_context: str = "", task_id: str = None) -> dict:
    """
    State-Aware Replanning with HITL Support (Phase 8).
    Treats 'HARD' constraints as non-negotiable.
    """
    feedback_type = feedback.get("type", "SYSTEM_FAILURE")
    reason = feedback.get("reason", "Unknown failure")
    priority = feedback.get("priority", "SOFT")
    
    constraint_prefix = "[HARD CONSTRAINT]" if priority == "HARD" else "[ADVISORY]"
    feedback_instruction = f"{constraint_prefix} {feedback.get('instruction', reason)}"

    replan_prompt = (
        f"Task: {task}\n"
        f"Previous Failure Type: {feedback_type}\n"
        f"Human/System Feedback: {feedback_instruction}\n\n"
        f"Memory Context: {memory_context}\n"
        "You are the Planner Agent in RECOVERY MODE.\n"
        "The previous approach failed or was rejected by a human.\n\n"
        "Rules:\n"
        "1. If feedback is HARD, you MUST change your tool selection or strategic logic.\n"
        "2. Provide a new structured plan [JSON].\n"
        "3. Ensure the new steps directly address the failure reason.\n"
        "Output JSON only: { \"strategy\": \"...\", \"constraints\": {...}, \"steps\": [...] }"
    )

    try:
        resp_data = call_llm(replan_prompt, system_prompt="You are a reflective strategist. Fix the plan based on feedback.", role="strong", task_id=task_id)
        resp_text = resp_data.get("content", "")
        plan_data = json.loads(_clean_json(resp_text), strict=False)
        # Prune constraints before returning
        plan_data["constraints"] = prune_constraints(plan_data.get("constraints", {}))
        return plan_data
    except:
        # Fallback to a safe search plan
        return {
            "strategy": "explore",
            "constraints": {"replan": True, "feedback": feedback_instruction},
            "steps": ["Readjust strategy based on feedback", "Synthesize safe answer"]
        }
