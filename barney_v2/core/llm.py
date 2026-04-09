"""
LLM Interface: Handles communication with the LLM.
"""

import os
import time
import re
from groq import Groq
from dotenv import load_dotenv

# Load credentials
load_dotenv()
_client_instance = None

from redis_client import check_llm_throttle, add_task_usage, get_task
from core.models import ModelRouter, MODEL_REGISTRY

def get_client():
    global _client_instance
    if _client_instance is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            print("  🚨 [llm] Error: GROQ_API_KEY not found in environment.")
            return None
        _client_instance = Groq(api_key=key)
    return _client_instance

def smart_trim(prompt: str, threshold: int = 20000) -> str:
    """Importance-Aware Pruning: Targets verbose tool outputs (Observations) (Phase 33)."""
    if len(prompt) <= threshold:
        return prompt
    
    import re
    print(f"  ⚠️ [llm] Prompt oversized ({len(prompt)} chars). Initiating Semantic Pruning.")
    
    # Target large Observation blocks (common source of bloat)
    # This keeps Thought and Step context intact
    observations = re.findall(r"(Observation:.*?)(?=\n\nThought:|\n\nStep:|$)", prompt, re.DOTALL)
    
    refined_prompt = prompt
    for obs in observations:
        if len(obs) > 4000:
            short_obs = obs[:2000] + "\n[... tool output truncated for brevity ...]\n" + obs[-2000:]
            refined_prompt = refined_prompt.replace(obs, short_obs)
    
    # Fallback to character-trimming if still too large
    if len(refined_prompt) > threshold:
        prefix = refined_prompt[:threshold // 2]
        suffix = refined_prompt[-threshold // 2:]
        return f"{prefix}\n\n[... content trimmed ...] \n\n{suffix}"
        
    return refined_prompt


def smart_trim(prompt: str, threshold: int = 20000) -> str:
    """Importance-Aware Pruning: Targets verbose tool outputs (Observations) (Phase 33)."""
    if len(prompt) <= threshold:
        return prompt
    
    import re
    print(f"  ⚠️ [llm] Prompt oversized ({len(prompt)} chars). Initiating Semantic Pruning.")
    
    # Target large Observation blocks (common source of bloat)
    # This keeps Thought and Step context intact
    observations = re.findall(r"(Observation:.*?)(?=\n\nThought:|\n\nStep:|$)", prompt, re.DOTALL)
    
    refined_prompt = prompt
    for obs in observations:
        if len(obs) > 4000:
            short_obs = obs[:2000] + "\n[... tool output truncated for brevity ...]\n" + obs[-2000:]
            refined_prompt = refined_prompt.replace(obs, short_obs)
    
    # Fallback to character-trimming if still too large
    if len(refined_prompt) > threshold:
        prefix = refined_prompt[:threshold // 2]
        suffix = refined_prompt[-threshold // 2:]
        return f"{prefix}\n\n[... content trimmed ...] \n\n{suffix}"
        
    return refined_prompt


def call_llm(prompt: str, system_prompt: str = "You are a helpful assistant.", role: str = "fast", task_id: str = None, task_type: str = "general", is_judge_call: bool = False, remaining_steps: int = 1) -> str:
    """Budget-Aware LLM Call: Handles routing, fallbacks, and quality verification (Phase 35)."""
    client = get_client()
    if not client: return {"status": "LLM_FAILURE", "error": "GROQ_API_KEY Missing"}
        
    # 1. Budget & Policy Resolution
    budget_remaining = 0.05
    if task_id:
        state = get_task(task_id) or {}
        budget_total = state.get("budget_usd", 0.05)
        metrics = state.get("metrics", {})
        cost_so_far = metrics.get("total_cost", 0.0)
        budget_remaining = budget_total - cost_so_far

    # 2. Semantic Guard (Skip for pure judges)
    safe_prompt = smart_trim(prompt) if not is_judge_call else prompt
    
    # 3. Decision Routing
    primary_model = ModelRouter.resolve_model(role, task_type=task_type, budget_remaining=budget_remaining, remaining_steps=remaining_steps)
    fallback_model = MODEL_REGISTRY["llama-3.1-8b-instant"]["id"]
    
    # Adversarial System Prompt for Judges (Phase 35/36)
    effective_system_prompt = system_prompt
    if is_judge_call:
        effective_system_prompt += (
            "\nADVERSARIAL_MANDATE: Be hyper-critical. Look for hallucinations and missing grounding.\n"
            "CITATION_REQUIRED: For every numeric claim or specific fact, cite the Step Index from history.\n"
            "If no evidence exists in history, label as 'UNVERIFIED'.\n"
            "Format: [Claim] | [Source: Step X] | [Status: VERIFIED/UNVERIFIED/CONTRADICTED]\n"
            "Provide 'Score: [0.0-10.0]' and 'Confidence: [0.0-1.0]'."
        )
    else:
        effective_system_prompt += "\nAlways include 'Confidence: [0.0-1.0]' at the end of your response."

    execution_stack = [primary_model]
    if primary_model != fallback_model:
        execution_stack.append(fallback_model)
    
    for model_id in execution_stack:
        is_fallback = (model_id == fallback_model and primary_model != fallback_model)
        attempt_log = f"(model={model_id})" if not is_fallback else f"(FALLBACK: {model_id})"
        
        if is_fallback:
             print(f"  🚨 [llm] Fallback triggered. Model downgraded to {model_id}.")
        
        print(f"  🧠 [llm] Attempting LLM call {attempt_log}...")
        
        MAX_RETRIES = 2
        for attempt in range(1, MAX_RETRIES + 1):
            # Global Throttle check (RPM logic)
            while check_llm_throttle(model_id):
                print(f"  ⏳ [llm] {model_id} throttled. Waiting...")
                time.sleep(1.0)

            try:
                call_start = time.time()
                completion = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": effective_system_prompt},
                        {"role": "user", "content": safe_prompt}
                    ],
                    temperature=0.1 if is_judge_call else 0.5,
                )
                
                duration = round(time.time() - call_start, 2)
                usage = completion.usage
                cost = ModelRouter.calculate_cost(model_id, usage.prompt_tokens, usage.completion_tokens)
                
                # Check for "Garbage" output on Fallback (Phase 34)
                content = completion.choices[0].message.content
                if is_fallback and (not content or len(content) < 50):
                     print("  ⚠️ [trust] Fallback produced shallow output. Retrying verify loop.")
                     # No return here, let it retry or fail
                     
                print(f"  🧠 [llm] Success ({duration}s, {usage.total_tokens} tokens, ${cost})")
                
                # 3. Telemetry Integration
                if task_id:
                    add_task_usage(task_id, usage.total_tokens, cost)
                
                # Confidence Extraction (Phase 35)
                conf_match = re.search(r"Confidence:\s*([0-9\.]+)", content)
                confidence = float(conf_match.group(1)) if conf_match else 0.7
                
                return {
                    "content": content,
                    "confidence": confidence,
                    "model": model_id
                }
                
            except Exception as e:
                backoff = 2 ** (attempt - 1)
                print(f"  ⚠️ [llm] {model_id} attempt {attempt} failed: {e}. Backoff {backoff}s")
                if attempt == MAX_RETRIES:
                    if model_id == fallback_model:
                        return {"status": "LLM_FAILURE", "reason": "TOTAL_PROVIDER_FAILURE", "error": str(e)}
                    print(f"  🚨 [llm] {model_id} failed catastrophically. Falling back to {fallback_model}...")
                    break # Trigger outer fallback loop
                time.sleep(backoff)
    
    return {"status": "LLM_FAILURE", "reason": "ROUTING_EXHAUSTED"}
