import json
import time
from datetime import datetime
from core.llm import call_llm

def get_grounding_requirement(task: str, task_id: str = None) -> dict:
    """
    Semantic Classifier: Determines if a task needs external grounding.
    Phase 40: Intent Intelligence.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    sys_prompt = (
        "You are the Intent Classifier for Barney v2.\n"
        f"Today's date is {current_date}.\n\n"
        "Analyze the user's task and determine if it requires external grounding (web search).\n"
        "Output MUST be a strict JSON object:\n"
        "{\n"
        "  \"required_grounding\": \"NONE\" | \"ARCHIVAL\" | \"RECENT\" | \"REAL_TIME\",\n"
        "  \"reasoning\": \"Why this level of grounding?\",\n"
        "  \"target_facts\": [\"fact 1 to find\", \"fact 2 to find\"],\n"
        "  \"temporal_anchor\": \"YYYY-MM-DD\"\n"
        "}\n\n"
        "- REAL_TIME: MANDATORY for weather, sports scores, stock prices, news, and anything happening 'today' or 'currently'.\n"
        "- RECENT: For events in the last week or month (e.g., 'who won the Oscar last month').\n"
        "- ARCHIVAL: For historical facts, biographical data, or research papers.\n"
        "- NONE: For static logic, math, creative writing, or stable general knowledge (e.g., 'who is the first president')."
    )

    user_prompt = f"Task: {task}"
    
    print(f"  🧠 [preprocessor] Analyzing intent for: {task[:50]}...")
    try:
        resp_data = call_llm(user_prompt, system_prompt=sys_prompt, role="fast", task_id=task_id)
        content = resp_data.get("content", "")
        
        # Robust JSON extraction
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == 0:
             raise ValueError("No JSON found in response")
             
        grounding_data = json.loads(content[start:end])
        grounding_data["temporal_anchor"] = current_date
        
        print(f"  🧠 [preprocessor] Grounding: {grounding_data.get('required_grounding')} | Facts: {len(grounding_data.get('target_facts', []))}")
        return grounding_data
    except Exception as e:
        print(f"  ⚠️ [preprocessor] Warning: Classification failed ({e}). Defaulting to NONE.")
        return {
            "required_grounding": "NONE",
            "reasoning": "Fallback due to classification error",
            "target_facts": [],
            "temporal_anchor": current_date
        }
