"""
Memory: The persistent storage for Barney v2 insights.

Stores atomized learnings and tracks performance scores based on 
Harsh Execution Success + Outcome Valuation mapping. (Stress Test Layer #4 & #6)
"""

import json
import os


class Memory:
    def __init__(self, filepath: str = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "memory.json")
        
        self.filepath = filepath
        self._store = []
        self._stats = {} # Cached stats
        self._load()

    def _load(self):
        """Load insights from memory.json."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self._store = json.load(f)
                print(f"  💾 [memory] Loaded {len(self._store)} insight(s).")
                # Immediate refresh (Stress Test #1)
                self.recompute_strategy_stats()
            except (json.JSONDecodeError, IOError):
                self._store = []

    def _save(self):
        """Persist current store to memory.json."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(self._store, f, indent=2)
        except IOError as e:
            print(f"  ❌ [memory] Save failed: {e}")

    def add(self, insight: dict):
        """Add insight and IMMEDIATE refresh stats (Stress Test #1)."""
        MAX_INSIGHTS = 50
        self._store.append(insight)
        if len(self._store) > MAX_INSIGHTS:
            self._store.pop(0)
        self._save()
        # Immediate refresh post-add
        self.recompute_strategy_stats()

    def count(self) -> int:
        return len(self._store)

    def clear(self):
        self._store = []
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        self._stats = {}
        print("  🧹 [memory] Cleared all insights.")

    def search(self, task: str) -> dict:
        """Context-Aware Search: Retrieve both tool insights and reasoning traces (Phase #4A)."""
        from core.insight_engine import get_task_type, get_task_condition, extract_intent
        t_type = get_task_type(task)
        condition = get_task_condition(task)
        task_keywords = set(task.lower().split())
        
        matches = []
        reason_traces = []
        
        # 1. Collect Matches
        for insight in self._store:
            # Match by Type or Condition
            type_match = insight.get("task_type") == t_type
            cond_match = insight.get("condition") == condition and condition != "general"
            
            if type_match or cond_match:
                matches.append(insight)
                
            # 2. Reasoning Memory Extraction (Final Fix #2)
            # Only consider successful outcomes for reasoning reuse
            if insight.get("outcome_score", 0) > 0:
                trace = insight.get("reason_trace")
                if trace:
                    # Alignment Check: Same type OR keyword overlap
                    insight_task = insight.get("task", "").lower()
                    overlap = any(kw in insight_task for kw in task_keywords if len(kw) > 3)
                    
                    if type_match or overlap:
                        reason_traces.append({
                            "trace": trace,
                            "score": insight.get("outcome_score", 0),
                            "timestamp": insight.get("timestamp", 0)
                        })

        # 3. Sort and Limit Traces (Recency First, then Score)
        reason_traces.sort(key=lambda x: (x["timestamp"], x["score"]), reverse=True)
        
        # Deduplicate and limit
        unique_traces = []
        seen = set()
        for rt in reason_traces:
            t_tuple = tuple(rt["trace"])
            if t_tuple not in seen:
                unique_traces.append(rt["trace"])
                seen.add(t_tuple)
            if len(unique_traces) >= 2: break

        return {
            "insights": matches,
            "reason_traces": unique_traces
        }

    def get_strategy_stats(self, current_timestamp: int) -> dict:
        """Returns the cached stats. Ensures they are fresh."""
        return self._stats

    def recompute_strategy_stats(self):
        """
        Calculate global strategy stats reflecting the Harsh Value Layer.
        Implements Pattern Amplification and Harsh Mapping. (Step #4 & #6)
        """
        STRATEGY_WEIGHTS = [0.5, 1.0, 2.0]
        current_timestamp = len(self._store)
        
        stats = {}
        
        # Track consecutive bad runs per strategy for Pattern Amplification (Step #6)
        consecutive_bad_counts = {}

        # Process from oldest to newest to track pattern amplification correctly
        for insight in self._store:
            trace = insight.get("strategy_trace", [])
            success = insight.get("success", False)
            outcome_score = insight.get("outcome_score", 0)
            cost = insight.get("cost", {"steps": 0, "tool_calls": 0})
            
            if not trace: continue
                
            age = max(0, current_timestamp - insight.get("timestamp", current_timestamp))
            decay = (0.9 ** age)
            
            # 1. Harsh Signaling Mapping (Step #4)
            # success + outcome=1  -> +2
            # success + outcome=-1 -> -1 (Garbage Success Penalty)
            # failure + outcome=1  -> 0
            # failure + outcome=-1 -> -2
            mapping = {
                (True, 1): 2.0,
                (True, -1): -1.0,
                (False, 1): 0.0,
                (False, -1): -2.0
            }
            # Handle the 0 (Weak) outcome implicitly as leaning toward bad or success depending on exec
            if outcome_score == 0:
                base_signal = 0.5 if success else -0.5
            else:
                base_signal = mapping.get((success, outcome_score), -1.0)
                
            seen_in_current_trace = set()
            for i, strategy in enumerate(trace):
                # 2. Pattern Amplification (Step #6)
                is_bad = outcome_score < 0
                if is_bad:
                    consecutive_bad_counts[strategy] = consecutive_bad_counts.get(strategy, 0) + 1
                else:
                    consecutive_bad_counts[strategy] = 0
                
                bad_runs = consecutive_bad_counts[strategy]
                # effective_score = base_score * (1 + consecutive_bad_runs * 0.5) (Step #6)
                # If negative score, this amplifies the penalty.
                effective_signal = base_signal
                if is_bad and base_signal < 0:
                     effective_signal *= (1 + (bad_runs - 1) * 0.5)

                weight_idx = len(STRATEGY_WEIGHTS) - (len(trace) - i)
                weight = STRATEGY_WEIGHTS[weight_idx] if weight_idx >= 0 else 0.5
                
                # --- MEMORY PROTECTION (Step #6) ---
                # Reduce contribution of bad results to prevent learning garbage
                if outcome_score < 0:
                    weight *= 0.5
                    
                point = effective_signal * weight * decay
                
                if strategy not in stats:
                    stats[strategy] = {
                        "score": 0.0, "count": 0, "total_steps": 0, "total_tools": 0, "total_outcome": 0,
                        "consecutive_bad": 0
                    }
                
                stats[strategy]["score"] += point
                
                if strategy not in seen_in_current_trace:
                    stats[strategy]["count"] += 1
                    stats[strategy]["total_steps"] += cost.get("steps", 0)
                    stats[strategy]["total_tools"] += cost.get("tool_calls", 0)
                    stats[strategy]["total_outcome"] += outcome_score
                    seen_in_current_trace.add(strategy)
            
            # Store final pattern state for selection fatigue
            for s in seen_in_current_trace:
                stats[s]["consecutive_bad"] = consecutive_bad_counts.get(s, 0)
        
        # 3. Compute Averages
        for s in stats:
            count = stats[s]["count"]
            stats[s]["avg_steps"] = stats[s]["total_steps"] / max(count, 1)
            stats[s]["avg_tools"] = stats[s]["total_tools"] / max(count, 1)
            stats[s]["avg_outcome"] = stats[s]["total_outcome"] / max(count, 1)
                
        self._stats = stats
