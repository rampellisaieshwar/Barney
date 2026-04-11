import json
from core.llm import call_llm

def _clean_json(text: str) -> str:
    """Robust JSON extraction from LLM response."""
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1:
        return text[first_brace:last_brace+1]
    return text.strip()

def decide_tool(task: str, task_id: str = None) -> dict:
    """
    Planner as a Decision Model.
    Decides the best tool to answer the user's query.
    """
    sys_prompt = (
        "You are a planning agent.\n"
        "Decide the best way to answer the user's query.\n\n"
        "Available tools:\n"
        "1. search -> for real-time, external, or unknown information (e.g. weather, news, today's prices)\n"
        "2. python -> for computations, sorting lists, writing code, executing logic\n"
        "3. llm -> for reasoning, historical explanations, general knowledge, summarizing\n\n"
        "Rules:\n"
        "- If the query requires current, real-world, or unknown information -> use search\n"
        "- If the query involves calculation -> use python\n"
        "- If the query can be answered from general knowledge -> use llm\n\n"
        "Return strictly JSON:\n"
        "{\n"
        "  \"tool\": \"search\" | \"python\" | \"llm\",\n"
        "  \"reason\": \"short explanation\",\n"
        "  \"confidence\": 0.95\n"
        "}"
    )

    print(f"  🧠 [planner] Deciding tool for task: {task[:50]}...")
    
    fallback_plan = {
        "tool": "llm",
        "reason": "fallback due to error",
        "confidence": 0.5
    }

    try:
        resp_data = call_llm(task, system_prompt=sys_prompt, role="fast", task_id=task_id)
        if resp_data is None:
            return fallback_plan

        resp_text = resp_data.get("content", "")
        plan_data = json.loads(_clean_json(resp_text), strict=False)
        
        # Enforce defaults if missing
        if "tool" not in plan_data: plan_data["tool"] = "llm"
        if "reason" not in plan_data: plan_data["reason"] = "No reason provided"
        if "confidence" not in plan_data: plan_data["confidence"] = 0.5

        return plan_data

    except Exception as e:
        print(f"  🧠 [planner] Error generating decision: {e}")
        return fallback_plan
