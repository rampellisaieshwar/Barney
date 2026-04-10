import redis
import os
import json
import time

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)

QUEUE_HIGH = "barney_task_high"
QUEUE_MEDIUM = "barney_task_medium"
QUEUE_LOW = "barney_task_low"

def enqueue_task(task_id: str, task: str, user_id: str = "anonymous", budget_usd: float = 0.05):
    """Atomic task submission with Deterministic Priority, Cost, and Budget (Phase 34)."""
    # 1. Classification logic (Fix #3: Priority Rule Override)
    task_lower = task.lower()
    priority = "LOW"
    cost = "LOW"
    target_queue = QUEUE_LOW
    
    # Priority Keywords
    if any(k in task_lower for k in ["urgent", "critical", "fix", "priority", "now"]):
        priority = "HIGH"
        target_queue = QUEUE_HIGH
    elif any(k in task_lower for k in ["research", "summarize", "analyze", "data"]):
        priority = "MEDIUM"
        target_queue = QUEUE_MEDIUM

    # Cost Keywords (Phase 28)
    if any(k in task_lower for k in ["research", "search", "web", "analyze"]):
        cost = "HIGH"
    elif any(k in task_lower for k in ["summarize", "write", "draft"]):
        cost = "MEDIUM"

    payload = json.dumps({
        "task_id": task_id,
        "task": task,
        "priority": priority,
        "cost": cost,
        "user_id": user_id,
        "budget_usd": budget_usd
    })
    
    # Set initial state with budget (Phase 34)
    update_task(task_id, "PENDING", user_id=user_id, budget_usd=budget_usd)
    
    # Push to correct queue
    redis_client.lpush(target_queue, payload)
    print(f"  📥 [redis] Enqueued {priority}/{cost} task (Budget: ${budget_usd}) for {user_id}: {task_id}")

def is_rate_limited(user_id: str, limit: int = 5, window: int = 60):
    """Atomic Rate Limiting using INCR + EXPIRE (Phase 29)."""
    key = f"rate_limit:{user_id}"
    count = redis_client.incr(key)
    
    if count == 1:
        redis_client.expire(key, window)
        
    return count > limit

def index_user_task(user_id: str, task_id: str):
    """Maintains a capped list of task IDs for a user history (Fix #1: Memory Leak)."""
    key = f"history:{user_id}"
    redis_client.lpush(key, task_id)
    # Kap at 100 items (Fix #1)
    redis_client.ltrim(key, 0, 99)

def get_user_history(user_id: str):
    """Retrieves full task objects for a user's recent history."""
    key = f"history:{user_id}"
    task_ids = redis_client.lrange(key, 0, -1)
    
    history = []
    for tid in task_ids:
        task = get_task(tid)
        if task:
            history.append({**task, "task_id": tid})
    return history

def dequeue_task_priority(skip_high: bool = False, timeout: int = 2):
    """Hybrid Blocking/Non-blocking multi-priority dequeue with 5-dimension context (Phase 30)."""
    
    # Helper to parse payload (Fix #1: Identity Extraction)
    def _parse(raw):
        if not raw: return None
        # raw is (queue_name, data) for brpop, or just data for rpop
        data_str = raw[1] if isinstance(raw, tuple) else raw
        data = json.loads(data_str)
        return (
            data.get("task_id"), 
            data.get("task"), 
            data.get("priority", "LOW"), 
            data.get("cost", "LOW"),
            data.get("user_id", "anonymous"),
            data.get("budget_usd", 0.05)
        )

    # Case 1: Fairness Mode
    if skip_high:
        for q in [QUEUE_MEDIUM, QUEUE_LOW]:
            task = _parse(redis_client.rpop(q))
            if task: return task
        return _parse(redis_client.rpop(QUEUE_HIGH))

    # Case 2: Normal Mode
    high_task = _parse(redis_client.rpop(QUEUE_HIGH))
    if high_task: return high_task

    raw = redis_client.brpop([QUEUE_MEDIUM, QUEUE_LOW], timeout=timeout)
    return _parse(raw)

def get_active_high_cost_count():
    """Returns total fleet-wide high-cost tasks currently running."""
    val = redis_client.get("barney_active_high_cost_count") or 0
    return int(val)

def change_active_high_cost_count(delta: int):
    """Atomics for cost tracking. Floor at 0 (Fix #1: Counter Recovery)."""
    new_val = redis_client.incrby("barney_active_high_cost_count", delta)
    if new_val < 0:
        redis_client.set("barney_active_high_cost_count", 0)
    return new_val

# --- Phase 31: Persistence & State Management ---
# (DELETED REDUNDANT update_task at line 125)

# --- Phase 32: Global LLM Stability Helpers ---

def check_llm_throttle(model_id: str = "llama-3.1-8b-instant", limit: int = None) -> bool:
    """True global rate limit (RPM logic) via Redis window. 
    Supports model-specific limits (Phase 33).
    """
    # Fallback to defaults if not provided (Phase 32 compat)
    if limit is None:
        limit = 30 if "8b" in model_id else 10
        
    key = f"llm_throttle:{model_id}:{int(time.time() / 60)}" # Per-minute window
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 65) # Slight overlap for window safety
    return count > limit

def add_task_usage(task_id: str, tokens: int, cost: float):
    """Atomically aggregates costs and tokens for a task (Phase 33)."""
    current = get_task(task_id) or {}
    metrics = current.get("metrics")
    if not isinstance(metrics, dict):
        metrics = {"total_tokens": 0, "total_cost": 0.0, "models": []}
    
    metrics["total_tokens"] = metrics.get("total_tokens", 0) + tokens
    metrics["total_cost"] = round(float(metrics.get("total_cost", 0.0)) + cost, 6)
    
    update_task(task_id, current.get("status", "RUNNING"), metrics=metrics)

def update_task(task_id: str, status: str, result=None, logs=None, worker_id: str = None, user_id: str = None, checkpoint: dict = None, metrics: dict = None, budget_usd: float = None):
    """Centralized state management with standard schema. 
    ENFORCES Identity, Checkpoints, Metrics, and Budgets (Phase 34).
    """
    current = get_task(task_id) or {}
    
    # Strictly preserve original user_id (Fix #4)
    final_user_id = current.get("user_id") if current.get("user_id") else (user_id if user_id else "anonymous")

    state = {
        "task_id": task_id,
        "status": status,
        "result": result if result is not None else current.get("result"),
        "logs": logs if logs is not None else current.get("logs", []),
        "worker_id": worker_id if worker_id else current.get("worker_id"),
        "user_id": final_user_id,
        "checkpoint": checkpoint if checkpoint else current.get("checkpoint"),
        "metrics": metrics if isinstance(metrics, dict) else (current.get("metrics") if isinstance(current.get("metrics"), dict) else {"total_tokens": 0, "total_cost": 0.0, "models": []}),
        "budget_usd": budget_usd if budget_usd is not None else current.get("budget_usd", 0.05),
        "updated_at": time.time()
    }
    redis_client.set(task_id, json.dumps(state))

# --- Phase 34: Intelligence Learning Store ---

def record_model_experience(task_type: str, model_id: str, quality_score: float):
    """Tracks model performance yield per domain (Phase 35).
    quality_score: 0.0 to 1.0 (converted from 0-10 judge score)
    """
    key = f"exp:{task_type}:{model_id}"
    # Use HINCRBYFLOAT for summing quality points
    redis_client.hincrbyfloat(key, "total_quality", quality_score)
    redis_client.hincrby(key, "run_count", 1)

def get_model_experience(task_type: str, model_id: str) -> float:
    """Returns average quality yield for a model in a specific territory."""
    key = f"exp:{task_type}:{model_id}"
    stats = redis_client.hgetall(key)
    if not stats: return 1.0 # Default to trust
    
    total_q = float(stats.get(b"total_quality", 0.0))
    runs = int(stats.get(b"run_count", 0))
    if runs == 0: return 1.0
    return total_q / runs

def get_throttle_pressure(model_id: str) -> int:
    """Estimates system load for the current model window."""
    key = f"llm_throttle:{model_id}:{int(time.time() / 60)}"
    return int(redis_client.get(key) or 0)

def append_log(task_id: str, message: str):
    """Safely appends a message to the task log and preserves overall state.
    Includes a cap to prevent memory bloat.
    """
    MAX_LOGS = 100
    state = get_task(task_id) or {}
    
    logs = state.get("logs", [])
    logs.append(message)
    
    # Apply cap
    if len(logs) > MAX_LOGS:
        logs = logs[-MAX_LOGS:]
        
    # Standard update while preserving status/result
    update_task(
        task_id, 
        state.get("status", "RUNNING"),
        state.get("result"),
        logs=logs
    )

def get_task(task_id: str):
    """Retrieve task state from Redis."""
    raw = redis_client.get(task_id)
    if not raw:
        return None
    return json.loads(raw)
# --- Phase 37: Strict Idempotency Layer ---

def acquire_step_lock(task_id: str, replan_counter: int, step_id: str, owner_token: str, ttl: int = 120) -> bool:
    """Atomic Distributed Lock with Ownership (SET NX EX)."""
    key = f"lock:{task_id}:{replan_counter}:{step_id}"
    return redis_client.set(key, owner_token, nx=True, ex=ttl)

def refresh_lock(task_id: str, replan_counter: int, step_id: str, owner_token: str, ttl: int = 120) -> bool:
    """Lua-based Lock Heartbeat: Only refreshes if owner matches."""
    key = f"lock:{task_id}:{replan_counter}:{step_id}"
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("expire", KEYS[1], ARGV[2])
    else
        return 0
    end
    """
    return bool(redis_client.eval(script, 1, key, owner_token, ttl))

def release_step_lock(task_id: str, replan_counter: int, step_id: str, owner_token: str) -> bool:
    """Lua-based Safe Delete: Prevents the 'Stolen Lock' bug."""
    key = f"lock:{task_id}:{replan_counter}:{step_id}"
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    return bool(redis_client.eval(script, 1, key, owner_token))

def save_step_result(task_id: str, replan_counter: int, step_id: str, result: dict, ttl: int = 604800):
    """Persists validated step results with 7-day TTL."""
    key = f"res:{task_id}:{replan_counter}:{step_id}"
    redis_client.set(key, json.dumps(result), ex=ttl)

def get_step_result(task_id: str, replan_counter: int, step_id: str) -> dict:
    """Retrieves versioned step results for idempotency checks."""
    key = f"res:{task_id}:{replan_counter}:{step_id}"
    raw = redis_client.get(key)
    return json.loads(raw) if raw else None

# --- Phase 37b: Tool-Level Idempotency ---

def save_tool_result(idempotency_key: str, result: any, ttl: int = 604800):
    """Caches individual tool results with a unique composite key."""
    key = f"tool_result:{idempotency_key}"
    redis_client.set(key, json.dumps(result), ex=ttl)

def get_tool_result(idempotency_key: str) -> any:
    """Retrieves cached tool output if available."""
    key = f"tool_result:{idempotency_key}"
    raw = redis_client.get(key)
    return json.loads(raw) if raw else None
