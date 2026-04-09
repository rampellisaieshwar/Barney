import threading
import time
import uuid
from core.loop import run_task
from redis_client import redis_client, get_task

def worker_thread(task_id, result_list):
    print(f"  👷 [worker] Starting execution for {task_id}")
    res = run_task("What is 15 * 12?", task_id=task_id)
    result_list.append(res)

if __name__ == "__main__":
    test_task_id = f"test_idempotency_{int(time.time())}"
    results = []
    
    # Clean Redis
    redis_client.delete(test_task_id)
    
    print(f"🚀 [test] Starting Multi-Worker Gauntlet for Task {test_task_id}")
    
    # Spawn 3 workers simultaneously
    threads = []
    for _ in range(3):
        t = threading.Thread(target=worker_thread, args=(test_task_id, results))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("\n📊 [test] Gauntlet Results:")
    for i, res in enumerate(results):
        print(f"  Worker {i+1} Status: {res.get('status')}")

    # Final Audit
    final_state = get_task(test_task_id)
    logs = final_state.get("logs", [])
    
    print("\n🔍 [test] Audit Summary:")
    executor_calls = [l for l in logs if "⚙️ [executor]" in l]
    cache_hits = [l for l in logs if "⏭️ [idempotency] Cache HIT" in l]
    
    print(f"  Total Executor Calls: {len(executor_calls)}")
    print(f"  Total Idempotency Cache Hits: {len(cache_hits)}")
    
    if len(executor_calls) == 1:
        print("\n✅ SUCCESS: Exactly-Once execution verified.")
    else:
        print("\n❌ FAILURE: Duplicate execution detected.")
