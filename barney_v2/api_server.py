from fastapi import FastAPI, HTTPException, Request, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import time
import os
import uuid
import json
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configure basic logging for observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger.info("🚀 Barney v2 API started")
logger.info("🔗 Connect to Redis at: " + str(os.getenv("REDIS_HOST", "localhost")))
logger.info("🧠 LLM interface ready")

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

@app.get("/")
def root():
    """PIPELINE CONTRACT: Root health check (Requirement #6)."""
    return {
        "status": "ok",
        "service": "barney-api",
        "version": "1.0.1"
    }

@app.get("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok"}

def _flatten_task_response(data: dict) -> dict:
    """PIPELINE CONTRACT: Ensures API responses always have 'answer' at top level.
    Redis stores: {"status": "DONE", "result": {"answer": "...", ...}, ...}
    API returns:  {"status": "DONE", "answer": "...", "confidence": ..., ...}
    """
    if not data:
        return data
    
    status = data.get("status", "PENDING")
    response = {
        "task_id": data.get("task_id"),
        "status": status,
        "logs": data.get("logs", []),
        "updated_at": data.get("updated_at"),
        "worker_id": data.get("worker_id"),
        "user_id": data.get("user_id"),
    }
    
    result = data.get("result")
    if not isinstance(result, dict): result = {}
    response["meta"] = result.get("meta", {})
    
    if status in ["DONE", "FAILED"]:
        if isinstance(result, dict):
            answer = result.get("answer", "")
            # Defensive: if answer is STILL a dict, stringify it
            if not isinstance(answer, str):
                answer = json.dumps(answer) if answer else ""
            response["answer"] = answer
            response["confidence"] = float(result.get("confidence", 0.0))
            response["steps"] = result.get("steps", 0)
            response["tools_used"] = result.get("tools_used", 0)
            response["response_time_ms"] = result.get("response_time_ms", 0)
            response["meta"] = result.get("meta", {})
        elif isinstance(result, str):
            response["answer"] = result
            response["confidence"] = 0.0
            response["meta"] = {}
        else:
            response["answer"] = "No answer generated."
            response["confidence"] = 0.0
            response["meta"] = {}
    else:
        # PENDING / RUNNING Consistency (Requirement #2)
        response["answer"] = ""
        response["message"] = "Thinking..."
        response["confidence"] = 0.0
        response["meta"] = {}
    
    return response

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
            update_task(task_id, "FAILED", {"answer": error_msg, "confidence": 0.0})
            # Return updated data
            data = get_task(task_id)

    # PIPELINE CONTRACT: Flatten response - extract answer from result to top level
    return _flatten_task_response(data)

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
            # PIPELINE CONTRACT: Use flattened structure for all states
            flat = _flatten_task_response(state)
            payload.update({
                "answer": flat.get("answer"),
                "confidence": flat.get("confidence"),
                "message": flat.get("message")
            })
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

@app.websocket("/ws/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: str):
    """Stream live logs for a task via WebSocket."""
    await websocket.accept()
    import asyncio
    last_index = 0
    try:
        while True:
            from redis_client import get_task
            task_data = get_task(task_id)
            if not task_data:
                await asyncio.sleep(0.5)
                continue

            logs = task_data.get("logs", [])
            for i in range(last_index, len(logs)):
                await websocket.send_json({
                    "type": "log",
                    "index": i,
                    "message": logs[i]
                })
            last_index = len(logs)

            status = task_data.get("status", "")
            if status in ("DONE", "FAILED"):
                answer = task_data.get("answer", "")
                confidence = task_data.get("confidence", 0)
                await websocket.send_json({
                    "type": "done",
                    "status": status,
                    "answer": answer,
                    "confidence": confidence
                })
                break

            await asyncio.sleep(0.3)
    except WebSocketDisconnect:
        pass

@app.get("/stream/{task_id}")
async def stream_task(task_id: str):
    """SSE endpoint for real-time task observability."""
    return StreamingResponse(
        stream_task_generator(task_id), 
        media_type="text/event-stream"
    )

from core.agent_mode.agent_creation_handler import set_agent_mode, is_agent_mode_on

class AgentModeRequest(BaseModel):
    user_id: str
    enabled: bool

@app.post("/agent_mode/toggle")
async def toggle_agent_mode(req: AgentModeRequest, x_api_key: str = Header(...)):
    """Toggle agent creation mode on or off for a user."""
    auth_key = os.getenv("BARNEY_API_KEY", "your-secret")
    if x_api_key != auth_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    set_agent_mode(req.user_id, req.enabled)
    state = "ON" if req.enabled else "OFF"
    return {"status": "ok", "agent_mode": state, "user_id": req.user_id}

@app.get("/agent_mode/status")
async def agent_mode_status(user_id: str, x_api_key: str = Header(...)):
    """Check if agent creation mode is currently on for a user."""
    auth_key = os.getenv("BARNEY_API_KEY", "your-secret")
    if x_api_key != auth_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"user_id": user_id, "agent_mode": "ON" if is_agent_mode_on(user_id) else "OFF"}
