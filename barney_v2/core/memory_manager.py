import json
import os
import time
import math
from core.llm import call_llm
from core.tools import DATA_ROOT
from core.memory_embeddings import embed_text, cosine_similarity, recency_score

LEDGER_PATH = os.path.join(DATA_ROOT, "knowledge_ledger.json")

def _load_ledger():
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, 'r') as f:
                return json.load(f)
        except: return []
    return []

def calculate_decay(base_confidence, timestamp_ns):
    """Temporal Decay: confidence * exp(-lambda * delta_t)."""
    now_ns = time.time_ns()
    delta_sec = (now_ns - timestamp_ns) / 1e9
    
    # Lambda for 50% decay over 7 days (~604800s)
    lam = -math.log(0.5) / 604800
    decay_factor = math.exp(-lam * delta_sec)
    
    decayed = base_confidence * decay_factor
    return max(0.1, decayed) # Floor at 0.1

def retrieve_similar(task, top_k=3):
    """Hybrid Semantic Retrieval: Vector Similarity + Confidence + Recency (Phase 25)."""
    ledger = _load_ledger()
    if not ledger: return []

    # 1. Embed incoming task (Fix #7: Safe handling)
    task_embedding = embed_text(task)
    if task_embedding is None:
        return [] # Fallback: No memory if embedding fails

    candidates = []
    for entry in ledger:
        # Calculate scores
        # A. Semantic Similarity
        entry_embedding = entry.get("embedding")
        sim = cosine_similarity(task_embedding, entry_embedding)
        
        # Threshold Check (Fix #5)
        if sim < 0.3:
            continue
            
        # B. Confidence (from ledger)
        conf = entry.get("confidence", 0.5)
        
        # C. Recency (Fix #4: Exponential Decay)
        recency = recency_score(entry.get("timestamp", 0))
        
        # Hybrid Score (Phase 25 Step 6)
        entry["hybrid_score"] = (sim * 0.6) + (conf * 0.3) + (recency * 0.1)
        candidates.append(entry)

    if not candidates: return []

    # 2. Rank and Limit
    candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    results = candidates[:top_k]
    
    # 3. Informative weighting for Planner (Adaptive Weighting)
    for r in results:
        r["effective_weight"] = r["hybrid_score"]

    return results

def detect_task_reuse(task, history):
    """Stagnation-Aware Task Reuse (Phase 12)."""
    # Simple similarity based on keyword overlap ratio
    task_words = set(task.lower().split())
    
    best_match = None
    max_sim = 0.0
    
    for past in history:
        past_task = past.get("task", "").lower()
        past_words = set(past_task.split())
        if not past_words: continue
        
        sim = len(task_words.intersection(past_words)) / max(len(task_words), len(past_words))
        if sim > max_sim:
            max_sim = sim
            best_match = past

    if max_sim > 0.85:
        # Check for stagnation
        reuse_count = best_match.get("reuse_count", 0)
        if reuse_count >= 2:
            return {"status": "FORCE_FRESH_STRATEGY", "reason": "Task reuse limit hit (Anti-Stagnation)."}
        
        return {"status": "REUSE_SUGGESTED", "match": best_match, "similarity": max_sim}
    
    return {"status": "NEW_TASK"}
