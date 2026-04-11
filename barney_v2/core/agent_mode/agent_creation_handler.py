"""
Agent Creation Handler
======================
Orchestrates the full agent-mode flow:
  1. Detect if task needs an external API
  2. Check if credential exists in vault
  3. If missing → return NEEDS_CREDENTIAL response
  4. If present → build and run tool → return answer
"""

from core.agent_mode.credential_vault import CredentialVault
from core.agent_mode.tool_builder_v2 import detect_required_credentials, build_and_run_tool

# Redis key for per-user toggle
AGENT_MODE_KEY = "agent_mode:{user_id}"

def is_agent_mode_on(user_id: str) -> bool:
    try:
        from redis_client import redis_client
        val = redis_client.get(AGENT_MODE_KEY.format(user_id=user_id))
        return val == b"on"
    except Exception:
        return False

def set_agent_mode(user_id: str, on: bool):
    from redis_client import redis_client
    key = AGENT_MODE_KEY.format(user_id=user_id)
    if on:
        redis_client.set(key, "on")
    else:
        redis_client.delete(key)


def handle(task: str, user_id: str) -> dict:
    """
    Main entry point called from loop.py when agent mode is ON.

    Returns one of:
      { "status": "NEEDS_CREDENTIAL", "answer": "<message to show user>", "credential_token": "..." }
      { "status": "DONE", "answer": "<final answer>" }
      { "status": "NO_API_NEEDED" }  ← tells loop.py to proceed normally
    """
    # Step 1: Detect if this task needs an external API
    detection = detect_required_credentials(task)

    if not detection.get("needs_api"):
        return {"status": "NO_API_NEEDED"}

    api_name = detection.get("api_name", "external API")
    token = detection.get("credential_token", "API_KEY")

    # Step 2: Check vault
    try:
        vault = CredentialVault()
    except ValueError as e:
        return {"status": "NO_API_NEEDED"}  # Vault not configured, fall through

    if not vault.has(token, user_id):
        # Step 3: Ask user for credential
        message = (
            f"🔑 I need your **{api_name} API key** to answer this.\n\n"
            f"Please re-ask your question like this:\n\n"
            f"`KEY={token}=your_actual_key_here {task}`\n\n"
            f"Your key will be stored securely and reused automatically next time."
        )
        return {
            "status": "NEEDS_CREDENTIAL",
            "answer": message,
            "credential_token": token,
            "confidence": 1.0
        }

    # Step 4: Resolve credential and run tool
    api_key = vault.resolve(token, user_id)
    credentials = {token: api_key}

    print(f"  🔧 [agent_mode] Building and running tool for: {task[:50]}")
    answer = build_and_run_tool(task, credentials)

    return {
        "status": "DONE",
        "answer": answer,
        "confidence": 0.9
    }
