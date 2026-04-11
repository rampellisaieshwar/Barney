import time
import json
from core import planner_agent, executor_agent
from core.memory import Memory
from core.scoring import calculate_depth_score, get_required_depth, SemanticEvaluator
from core.grounding import RealityAnchor
from redis_client import get_task, update_task, append_log

_memory = Memory()

def get_memory() -> Memory:
    return _memory

def looks_realtime(task: str) -> bool:
    """Validator: Check if the query implies real-time data needs."""
    REALTIME_HINTS = ["today", "latest", "now", "current", "live", "price", "score"]
    return any(w in task.lower() for w in REALTIME_HINTS)

def run_task(task: str, mode: str = "real", state_dict: dict = None, test_mode: bool = False, forced_outcome: dict = None, task_id: str = None) -> dict:
    """
    Linear Execution Pipeline (Phase 38: Controlled Autonomy).
    Pipeline: User Query -> Planner -> Validator -> Dispatcher -> Result
    """
    run_start_time = time.time()
    if task_id:
        update_task(task_id, "RUNNING")
        append_log(task_id, f"🚀 [Pipeline] Task started: {task[:50]}")

    # --- 1. PLANNER (LLM Decision) ---
    if task_id:
        append_log(task_id, "🧠 [Planner] Analyzing task to decide strategy...")
        
    plan = planner_agent.decide_tool(task, task_id)
    
    # --- 2. VALIDATOR (Guardrails) ---
    VALID_TOOLS = {"search", "python", "llm"}
    original_tool = plan.get("tool", "llm")
    
    if plan["tool"] not in VALID_TOOLS:
         plan["tool"] = "llm"
         
    overridden = False

    # Rule: If it asks for real-time info but chose LLM, correct it to 'search'.
    if plan["tool"] == "llm" and looks_realtime(task):
         plan["tool"] = "search"
         overridden = True
         if task_id:
             append_log(task_id, f"🛡️ [Validator] Overriding LLM to 'search' due to real-time keywords.")

    # Logging the decision as requested
    decision_log = {
         "task": task,
         "tool": plan["tool"],
         "confidence": plan.get("confidence", 0.5),
         "overridden": overridden,
         "original_tool": original_tool,
         "reason": plan.get("reason", "")
    }
    print("📝 [Decision Log]:", decision_log)
    if task_id:
         append_log(task_id, f"📋 [Decision Log] {json.dumps(decision_log)}")

    # --- 3. EXECUTOR (Dispatcher) ---
    if task_id:
         append_log(task_id, f"⚡ [Dispatcher] Routing task to '{plan['tool']}' tool...")
         
    exec_res = executor_agent.dispatch_tool(plan["tool"], task, task_id=task_id)

    # --- 4. FINAL RESPONSE ---
    final_answer = exec_res.get("answer", "No answer generated.")
    final_conf = exec_res.get("confidence", 0.5)

    response_time_ms = int((time.time() - run_start_time) * 1000)

    result_data = {
        "status": "DONE",
        "answer": final_answer,
        "confidence": final_conf,
        "tools_used": 1 if plan["tool"] != "llm" else 0,
        "response_time_ms": response_time_ms,
        "quality_tier": "PASSED"
    }

    if task_id:
        update_task(task_id, "DONE", result_data, checkpoint=None)
        append_log(task_id, f"🏁 [Pipeline] Task completed in {response_time_ms}ms")

    return result_data
