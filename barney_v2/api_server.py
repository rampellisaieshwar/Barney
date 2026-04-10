from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import time
import os
import uuid
import json
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("🚀 Barney v2 API started")
print("🔗 Connect to Redis at: " + str(os.getenv("REDIS_HOST", "localhost")))
print("🧠 LLM interface ready")

from redis_client import (
    enqueue_task, get_task, is_rate_limited, 
    index_user_task, get_user_history
)

app = FastAPI(title="Barney v2 Production API", version="1.0.1")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok"}

class TaskRequest(BaseModel):
    task: str
    user_id: str # Required in Phase 29
    budget_usd: float = 0.05 # Phase 34: Intelligence ceiling

@app.post("/run_task")
def run_task_api(request: TaskRequest, req: Request):
    """Submits a task with Rate Limiting (5/min) and User Indexing."""
    
    auth_key = os.getenv("BARNEY_API_KEY", "your-secret")
    if req.headers.get("x-api-key") != auth_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 1. Rate Limit Enforcement (Fix #2: Atomic Window)
    if is_rate_limited(request.user_id):
        raise HTTPException(
            status_code=429, 
            detail="Too many tasks. Limit: 5 per minute."
        )

    task_id = str(uuid.uuid4())
    
    try:
        # Enqueue with identity and budget (Phase 34)
        enqueue_task(task_id, request.task, user_id=request.user_id, budget_usd=request.budget_usd)
        
        # Index for history lookup (Fix #3)
        index_user_task(request.user_id, task_id)
        
        return {
            "task_id": task_id,
            "user_id": request.user_id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue task: {str(e)}")

@app.get("/status/{task_id}")
def get_status(task_id: str):
    """Retrieves the current state of a task from Redis with Zombie Detection."""
    data = get_task(task_id)

    if not data:
        raise HTTPException(status_code=404, detail="Task not found")

    # Zombie Detection (Phase 26): Recovery logic for crashed workers
    status = data.get("status")
    updated_at = data.get("updated_at", 0)
    
    if status == "RUNNING" and (time.time() - updated_at) > 120:
        # Re-verify to avoid race conditions (User Fix #2)
        fresh_data = get_task(task_id)
        if fresh_data.get("status") == "RUNNING" and (time.time() - fresh_data.get("updated_at", 0)) > 120:
            print(f"  🚨 [zombie] Task {task_id} stale for {int(time.time() - updated_at)}s. Failing.")
            from redis_client import update_task, append_log
            error_msg = "🚨 System failure: Task heartbeat lost (Worker timeout/crash)."
            append_log(task_id, error_msg)
            update_task(task_id, "FAILED", {"error": "worker_timeout"})
            # Return updated data
            return get_task(task_id)

    return data

async def stream_task_generator(task_id: str):
    """Event generator for Server-Sent Events (SSE). 
    Yields incremental logs and status updates.
    """
    last_len = 0
    
    while True:
        state = get_task(task_id)
        if not state:
            yield "data: {\"error\": \"Task not found\"}\n\n"
            break
            
        logs = state.get("logs", [])
        status = state.get("status", "PENDING")
        
        # Only send if there are new logs or status changed to terminal
        if len(logs) > last_len or status in ["DONE", "FAILED"]:
            new_logs = logs[last_len:]
            payload = {
                "status": status,
                "logs": new_logs,
                "full_count": len(logs)
            }
            yield f"data: {json.dumps(payload)}\n\n"
            last_len = len(logs)
            
        if status in ["DONE", "FAILED"]:
            break
            
        await asyncio.sleep(1)

@app.get("/tasks/{user_id}")
def get_user_tasks(user_id: str):
    """Retrieves chronological task history for a specific user (Capped at 100)."""
    try:
        history = get_user_history(user_id)
        return {
            "user_id": user_id,
            "count": len(history),
            "tasks": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.get("/stream/{task_id}")
async def stream_task(task_id: str):
    """SSE endpoint for real-time task observability."""
    return StreamingResponse(
        stream_task_generator(task_id), 
        media_type="text/event-stream"
    )
