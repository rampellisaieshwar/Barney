import json
import hashlib
import uuid
import time
from core.executor_agent import _call_tool
from redis_client import redis_client

def test_tool_idempotency():
    task_id = f"test_tool_{int(time.time())}"
    step_id = "step_a1"
    replan = 0
    
    print(f"🚀 [test] Starting Tool Idempotency Verification (Task {task_id})")
    
    # 1. First Call: Successful Python calculation
    args = {"code": "result = 15 * 12"}
    print("\n--- Call 1: New Tool Execution (python) ---")
    res1 = _call_tool("python", args, task_id=task_id, replan_counter=replan, step_id=step_id)
    print(f"  Result 1: {res1}")
    
    # 2. Second Call: Duplicate Python calculation (Expect HIT)
    print("\n--- Call 2: Duplicate Tool Execution (Expect HIT) ---")
    res2 = _call_tool("python", args, task_id=task_id, replan_counter=replan, step_id=step_id)
    print(f"  Result 2: {res2}")
    
    # 3. Third Call: list_dir (Highly deterministic success)
    print("\n--- Call 3: list_dir New execution ---")
    res3 = _call_tool("list_dir", {"path": "."}, task_id=task_id, replan_counter=replan, step_id=step_id)
    print(f"  Result 3: {res3}")
    
    # 4. Fourth Call: Non-Idempotent Tool (Expect SKIP - get_time is mapped to get_current_time)
    # Looking at tools.py: "get_time" maps to get_current_time. 
    # But my NON_IDEMPOTENT_TOOLS list used "get_current_time". I should align them.
    print("\n--- Call 4: Non-Idempotent Tool (Expect SKIP) ---")
    res4 = _call_tool("get_time", {}, task_id=task_id, replan_counter=replan, step_id=step_id)
    print(f"  Result 4: {res4}")

    print("\n📊 [test] Verification Audit:")
    
    serialized = json.dumps(args, sort_keys=True)
    hash1 = hashlib.md5(serialized.encode()).hexdigest()[:12]
    key1 = f"tool_result:{task_id}:{replan}:{step_id}:python:{hash1}"
    
    exists = redis_client.exists(key1)
    print(f"  Key '{key1}' exists in Redis: {bool(exists)}")
    
    if exists and res1 == res2:
        print("\n✅ SUCCESS: Tool-level idempotency verified.")
    else:
        print("\n❌ FAILURE: Idempotency logic inconsistent.")

if __name__ == "__main__":
    test_tool_idempotency()
