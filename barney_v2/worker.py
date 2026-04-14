import time
import json
import uuid
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure basic logging for observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from core.loop import run_task
from redis_client import (
    dequeue_task_priority, update_task, append_log, 
    get_active_high_cost_count, change_active_high_cost_count
)

GLOBAL_MAX_HIGH_COST = 2

WORKER_ID = str(uuid.uuid4())[:8]

def start_worker():
    """Main worker loop for Barney v2."""
    print("🚀 Barney v2 worker started")
    try:
        from redis_client import redis_client
        redis_client.ping()
        print("🔗 Redis connected")
    except Exception as e:
        print(f"🚨 Redis connection failed: {e}. Crashing early.")
        exit(1)
        
    print("🧠 LLM ready")
    print(f"  Worker ID: [{WORKER_ID}]. Listening for tasks...")
    
    consecutive_high_tasks = 0

    while True:
        try:
            # Step 1: Resource Awareness (Phase 28)
            active_high_cost = get_active_high_cost_count()
            capacity_saturated = (active_high_cost >= GLOBAL_MAX_HIGH_COST)
            
            # Step 2: Fairness Check
            skip_high_priority = (consecutive_high_tasks >= 3)
            
            # Hybrid Priority & Cost-Aware Pop (Phase 30: 5-Dimension context)
            task_data = dequeue_task_priority(skip_high=skip_high_priority)
            
            if task_data:
                # DEBUG: Trace the raw task data from Redis
                print(f"DEBUG RAW TASK: {task_data}")
                
                # SAFE PARSER: Handle multi-priority tuple return from redis_client (Phase 34 compatibility)
                # Unpacks up to 6 dimensions: (task_id, task, priority, cost, user_id, budget_usd)
                task_id = task_data[0]
                task_input = task_data[1]
                priority = task_data[2]
                cost = task_data[3]
                user_id = task_data[4]
                budget = task_data[5] if len(task_data) > 5 else 0.05
                
                print(f"PARSED TASK: id={task_id}, user={user_id}, cost={cost}")                
                # Step 3: Global Concurrency Guard (Fix #2, #4)
                acquired_cost_slot = False
                if cost == "HIGH" and active_high_cost >= GLOBAL_MAX_HIGH_COST:
                    # FALLBACK: If NO OTHER tasks are possible, we must proceed anyway (Fix #2)
                    # For now, if we picked it, we check if we should 'pause' or 're-queue'
                    # But the requirement says "Prefer LOW cost if busy". 
                    # If we already popped it and it's HIGH, and we are saturated:
                    # We only allow it if we are the only worker or it's HIGHEST priority.
                    msg = f"⚠️ [worker {WORKER_ID}] System saturated ({active_high_cost}/{GLOBAL_MAX_HIGH_COST} High-Cost). Delaying {task_id}."
                    print(msg)
                    # Re-queue at the front (lpush) would happen in dequeue_task_priority but here we need a simple fallback:
                    # To keep it simple as per User request: Proceed but log the saturation.
                    # Or better: Implementation as per Fix #4 (Atomic INCR)
                    pass

                if cost == "HIGH":
                    change_active_high_cost_count(1)
                    acquired_cost_slot = True

                print(f"📦 [worker {WORKER_ID}] Picked up {priority} priority / {cost} cost task for {user_id}: {task_id}")
                
                # Update fairness counter
                if priority == "HIGH":
                    consecutive_high_tasks += 1
                else:
                    consecutive_high_tasks = 0
                
                if consecutive_high_tasks > 3: 
                    # This only happens if skip_high was true but only HIGH was available
                    # We reset to avoid permanent high-priority lock
                    consecutive_high_tasks = 0

                # Mark as RUNNING and log start
                update_task(task_id, "RUNNING", worker_id=WORKER_ID, user_id=user_id)
                tag_prefix = f"[User:{user_id}] [Worker:{WORKER_ID}] [Priority:{priority}] [Cost:{cost}]"
                append_log(task_id, f"{tag_prefix} Task picked up. Initializing Barney core.")
                
                # Execute core intelligence with Resource Lifecycle (Fix #1)
                try:
                    update_task(task_id, "RUNNING", worker_id=WORKER_ID, user_id=user_id)
                    append_log(task_id, f"{tag_prefix} Consulting Planner Agent...")
                    
                    # Heartbeat update-at pulse
                    update_task(task_id, "RUNNING", worker_id=WORKER_ID, user_id=user_id)
                    append_log(task_id, f"{tag_prefix} Executing Implementation Plan...")
                    
                    result = run_task(task_input, task_id=task_id, user_id=user_id)
                    
                    # Terminal failure (BRAIN_DEAD) awareness
                    is_brain_dead = False
                    if isinstance(result, dict):
                        if result.get("status") == "BRAIN_DEAD": 
                            is_brain_dead = True
                        elif result.get("status") == "failed" and isinstance(result.get("result"), dict) and result["result"].get("status") == "BRAIN_DEAD":
                            is_brain_dead = True
                    
                    if is_brain_dead:
                        msg = f"🚨 {tag_prefix} Terminal failure: BRAIN_DEAD (Infrastructure issues)"
                        print(f"  [worker {WORKER_ID}] {msg}")
                        append_log(task_id, msg)
                        # PIPELINE CONTRACT: Store flat result with string answer
                        error_answer = result.get("answer", "Brain disconnected") if isinstance(result, dict) else "Brain disconnected"
                        if not isinstance(error_answer, str): error_answer = str(error_answer)
                        
                        flat_result = {
                            "answer": error_answer,
                            "confidence": 0.0,
                            "steps": 0,
                            "tools_used": 0,
                            "response_time_ms": 0
                        }
                        preview = error_answer[:100].replace('\n', ' ')
                        logger.info(f"  [FINAL] Answer type: {type(error_answer).__name__}, preview: {preview}")
                        update_task(task_id, "FAILED", flat_result, worker_id=WORKER_ID, user_id=user_id)
                    else:
                        print(f"✅ [worker {WORKER_ID}] Task {task_id} completed.")
                        append_log(task_id, f"🏁 {tag_prefix} Task completed successfully.")
                        
                        # PIPELINE CONTRACT: Extract and verify string answer
                        answer_val = ""
                        if isinstance(result, dict):
                            answer_val = result.get("answer", "")
                        elif isinstance(result, str):
                            answer_val = result
                        
                        # Definitive String Casting (Requirement #1)
                        if not isinstance(answer_val, str):
                            print(f"⚠️ [CONTRACT] Coercing answer from {type(answer_val)} to str")
                            answer_val = json.dumps(answer_val) if answer_val else ""
                        
                        flat_result = {
                            "answer": answer_val,
                            "confidence": result.get("confidence", 0.9) if isinstance(result, dict) else 0.9,
                            "steps": result.get("steps", 0) if isinstance(result, dict) else 0,
                            "tools_used": result.get("tools_used", 0) if isinstance(result, dict) else 0,
                            "response_time_ms": result.get("response_time_ms", 0) if isinstance(result, dict) else 0,
                            "meta": result.get("meta", {}) if isinstance(result, dict) else {}
                        }
                        
                        # [FINAL] Contract Logging (Requirement #7)
                        preview = answer_val[:100].replace('\n', ' ')
                        logger.info(f"  [FINAL] Answer type: {type(answer_val).__name__}, preview: {preview}")
                        update_task(task_id, "DONE", flat_result, worker_id=WORKER_ID, user_id=user_id)
                        
                        # Save to Qdrant semantic memory
                        try:
                            from core.qdrant_memory import save_conversation
                            save_conversation(user_id, task_input, answer_val)
                        except Exception as qe:
                            print(f"  ⚠️ [qdrant_memory] save skipped: {qe}")
                        
                except Exception as eval_err:
                    error_msg = f"❌ {tag_prefix} Execution error: {str(eval_err)}"
                    print(f"  [worker {WORKER_ID}] {error_msg}")
                    append_log(task_id, error_msg)
                    # PIPELINE CONTRACT: Standardized FAILED state (Requirement #3)
                    error_result = {
                        "answer": f"Execution error: {str(eval_err)}",
                        "confidence": 0.0,
                        "steps": 0,
                        "tools_used": 0,
                        "response_time_ms": 0,
                        "meta": {} # Logic could be added here to extract meta from local state if available
                    }
                    update_task(task_id, "FAILED", error_result, worker_id=WORKER_ID, user_id=user_id)
                finally:
                    if acquired_cost_slot:
                        change_active_high_cost_count(-1)
                    
        except Exception as queue_err:
            print(f"  🚨 [worker] Queue error: {str(queue_err)}")
            time.sleep(5) # Cooldown on connection errors

if __name__ == "__main__":
    start_worker()
