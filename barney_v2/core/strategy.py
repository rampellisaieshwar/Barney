"""
Strategy Module: Determines the execution approach for a task.

Implements selection hierarchy (Local → Value-Aware Global → Default)
with Strategy Locking (Step #2) and Strategy Fatigue (Step #5).
"""

import hashlib


COMPATIBLE_DOMAINS = {
    "web": ["web", "general"],
    "compute": ["compute", "general"],
    "file": ["file"],
    "general": ["general", "web", "compute"]
}

STRATEGY_PRIORITY = ["validate", "rank", "compare", "search"]

# Strategy Locking Cache (Step #2)
_strategy_cache = {}


def get_heuristic_prior(task: str) -> dict:
    """Corrected Heuristics: Weighted competition scores (Step #1)."""
    task = task.lower()
    scores = {}

    if any(k in task for k in ["compare", "difference", "vs", "better"]):
        scores["compare"] = 0.6
        scores["rank"] = 0.5

    if any(k in task for k in ["best", "top", "recommend"]):
        scores["rank"] = 0.6

    if any(k in task for k in ["why", "explain", "debug", "fix", "calculate", "math", "sum", "compute"]):
        scores["validate"] = 0.7 # High affinity for validation/computation

    if any(k in task for k in ["find", "list", "search"]):
        scores["search"] = 0.5

    return scores


def get_fatigue_multiplier(consecutive_bad_runs: int) -> float:
    """Nonlinear Fatigue Penalty (Step #5). Multiplier = 0.8^n."""
    if consecutive_bad_runs <= 0:
        return 1.0
    return 0.8 ** consecutive_bad_runs


def select_strategy(task: str, memory_insights: list, global_stats: dict = None, test_mode: bool = False) -> dict:
    """
    Select execution strategy using Strategy Locking and Fatigue.
    (Step #2 & Step #5)
    """
    if len(task) < 100 and "explain" in task.lower():
        return {
            "strategy": "direct", "warning": "Fast track",
            "suggested_strategy": "direct", "confidence": 1.0, "avg_steps": 1.0
        }
    # ── 2. Normalized Task Complexity ────────────────────────────────
    task_words = task.split()
    complexity = len(task_words)
    baseline_steps = 3 if complexity < 6 else 6

    # ── 3. Local Performance check ──────────────────────────────────
    local_score = 0
    for ins in memory_insights:
        if ins.get("success"):
            local_score += 1
        else:
            local_score -= 1

    if local_score < 0:
        return {
            "strategy": "explore", "warning": "⚠️ Local failures detected.",
            "suggested_strategy": None, "confidence": 0.0, "avg_steps": 0.0
        }

    # ── 4. Global Judgment (Valuation + Fatigue) ────────────────────
    heuristic_priors = get_heuristic_prior(task)
    combined_candidates = []
    active_strategies = set(list(heuristic_priors.keys()) + list((global_stats or {}).keys()))
    
    for s in active_strategies:
        h_score = heuristic_priors.get(s, 0.0)
        m_stat = (global_stats or {}).get(s, {
            "score": 0.0, "count": 0, "avg_steps": 0.0, "avg_tools": 0.0, "avg_outcome": 0.0,
            "consecutive_bad": 0
        })
        m_score = m_stat["score"]
        m_count = m_stat["count"]
        m_avg_steps = m_stat["avg_steps"]
        m_avg_tools = m_stat["avg_tools"]
        m_avg_outcome = m_stat["avg_outcome"]
        consecutive_bad = m_stat["consecutive_bad"]
        
        conf = max(0.0, min(1.0, m_score / max(m_count, 1)))
        
        if m_count < 3:
            f_score = (h_score * 0.7) + (m_score * 0.3)
        else:
            f_score = (h_score * 0.3) + (m_score * 0.7)
            
        # 4.1 Nonlinear Fatigue Penalty (Step #5)
        # Apply multiplier based on consecutive bad outcomes
        fatigue = get_fatigue_multiplier(consecutive_bad)
        if fatigue < 1.0:
            print(f"  📉 [fatigue] Strategy '{s}' penalized by {100*(1-fatigue):.1f}% due to {consecutive_bad} bad runs.")
        f_score *= fatigue
            
        combined_candidates.append({
            "strategy": s,
            "final_score": f_score,
            "confidence": conf,
            "count": m_count,
            "avg_steps": m_avg_steps,
            "avg_tools": m_avg_tools,
            "avg_outcome": m_avg_outcome,
            "cost_score": m_avg_steps + (m_avg_tools * 1.5)
        })

    if combined_candidates:
        combined_candidates.sort(key=lambda x: -x["final_score"])
        best = combined_candidates[0]
        
        # 5. Tie-Breaking & Efficiency Margin
        if len(combined_candidates) > 1:
            second = combined_candidates[1]
            gap = best["final_score"] - second["final_score"]
            if gap < 0.2:
                if second["cost_score"] < best["cost_score"]:
                    best = second

        # 6. Regret Calculation & Protection
        simpler_options = [c for c in combined_candidates if c["strategy"] != best["strategy"]]
        simpler_options.sort(key=lambda x: STRATEGY_PRIORITY.index(x["strategy"]) if x["strategy"] in STRATEGY_PRIORITY else 99, reverse=True)
        
        if simpler_options:
            simpler = simpler_options[0]
            regret = best["avg_steps"] - simpler["avg_steps"]
            
            is_reliable = best["confidence"] > 0.8
            is_valuable = best["avg_outcome"] > 0.0
            
            if not is_reliable and not is_valuable and regret > 1.5 and best["confidence"] < 0.7:
                best = simpler

        # 7. RECOVERY MODE (Emergency Path)
        # If confidence is low but intent is high, or we are failing, override fear.
        # Cooldown is handled by global_stats avg_outcome improvement.
        in_recovery = (best["count"] >= 3 and best["confidence"] < 0.6) or (best["avg_outcome"] < 0.0)
        
        if in_recovery:
            # Shift hierarchy: Intent/Heuristic > Memory
            # We add a 0.4 boost to heuristic-favored structured strategies
            if best["strategy"] in ["compare", "rank", "validate"]:
                print(f"  🚨 [recovery] Forced structure due to low confidence ({best['confidence']:.2f})")
                best["final_score"] += 0.4 # Forced Structure
            else:
                # If the best was 'search' but it failed, shift to 'compare/rank'
                for alt in combined_candidates:
                    if alt["strategy"] in ["compare", "rank"]:
                        alt["final_score"] += 0.5
                combined_candidates.sort(key=lambda x: -x["final_score"])
                best = combined_candidates[0]
                print(f"  🚨 [recovery] Pivoted to '{best['strategy']}' for stability.")

        # DELETED: Forced 'explore' downgrade that caused paralysis.

        print(f"  🎯 [strategy] Selected: {best['strategy']} | Score: {best['final_score']:.2f} | Conf: {best['confidence']:.2f}")

        # Cache suggestion if in test mode (Step #2)
        if test_mode:
            task_hash = hashlib.md5(task.encode()).hexdigest()
            _strategy_cache[task_hash] = best["strategy"]

        return {
            "strategy": "reuse_tools",
            "warning": f"📨 Strategy selected: '{best['strategy']}'. [MIN_SOURCES=2 Enforcement Active]",
            "suggested_strategy": best["strategy"],
            "confidence": best["confidence"],
            "avg_steps": best["avg_steps"]
        }

    return {
        "strategy": "explore", "warning": "🎯 No strong pattern found.",
        "suggested_strategy": None, "confidence": 0.0, "avg_steps": 0.0
    }
