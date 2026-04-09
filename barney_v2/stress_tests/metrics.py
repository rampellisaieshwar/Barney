"""
Metrics: Tracking cognitive stability, stubbornness, and recovery latency.
(Stress Test Layer #9)
"""

class MetricTracker:
    def __init__(self):
        self.history = []
        self.previous_strategy = None
        self.previous_outcome = None

    def log_run(self, cycle: int, strategy: str, outcome: int):
        """Record a test cycle and detect transitions (Judgment Layer #2 & #5)."""
        # 1. Switch Detection (Sharpened #2: (current != previous))
        switched = (strategy != self.previous_strategy) if self.previous_strategy else False
        
        # 2. Improvement Detection (Sharpened #5: (current_outcome > previous))
        improved = (outcome > self.previous_outcome) if self.previous_outcome is not None else False
        
        # 3. Bad Reuse Detection (Sharpened #2: Same strategy + Bad Outcome)
        bad_reuse = (not switched and outcome < 0)
        
        self.history.append({
            "cycle": cycle,
            "strategy": strategy,
            "outcome": outcome,
            "switched": switched,
            "improved": improved,
            "bad_reuse": bad_reuse
        })
        
        self.previous_strategy = strategy
        self.previous_outcome = outcome
        
        return {
            "switched": switched,
            "improved": improved,
            "bad_reuse": bad_reuse
        }

    def compute_stability_report(self) -> dict:
        """Calculate final cognitive health metrics (Judgment Layer #9)."""
        if not self.history:
            return {}
            
        total_runs = len(self.history)
        bad_reuses = sum(1 for h in self.history if h["bad_reuse"])
        
        # Stubbornness Index: (Failing Reuses / Total Runs) (Step #9)
        stubbornness_index = bad_reuses / total_runs if total_runs > 0 else 0.0
        
        # Recovery Latency: (First cycle switch after failure) (Step #9)
        # Find first run where outcome < 0. Then find first run after that where strategy switched.
        latency = 0
        first_fail_idx = -1
        for i, h in enumerate(self.history):
            if h["outcome"] < 0:
                first_fail_idx = i
                break
        
        if first_fail_idx != -1:
            for i in range(first_fail_idx + 1, len(self.history)):
                if self.history[i]["switched"]:
                    latency = i - first_fail_idx
                    break
            else:
                latency = len(self.history) - first_fail_idx # Never switched

        # Regret Persistence: (Consecutive bad decisions after penalty) (Measure #3)
        # Sequence of Bad Reuse
        regret_persistence = 0
        current_persistence = 0
        for h in self.history:
            if h["bad_reuse"]:
                current_persistence += 1
                regret_persistence = max(regret_persistence, current_persistence)
            else:
                current_persistence = 0

        # Failure Escape Rate (Step #9)
        total_failures = sum(1 for h in self.history if h["outcome"] < 0)
        successful_pivots = sum(1 for h in self.history if h["switched"] and h["improved"])
        escape_rate = successful_pivots / max(total_failures, 1)

        return {
            "stubbornness_index": stubbornness_index,
            "recovery_latency": latency,
            "regret_persistence": regret_persistence,
            "failure_escape_rate": escape_rate,
            "total_runs": total_runs
        }

    def print_summary(self):
        """Print the cycle comparison table."""
        print("\n" + "="*80)
        print(f"{'Cycle':<8} | {'Strategy':<12} | {'Outcome':<8} | {'Switched':<10} | {'Improved':<10}")
        print("-" * 80)
        for h in self.history:
            s_name = str(h['strategy']) if h['strategy'] is not None else "explore"
            o_val = str(h['outcome'])
            print(f"{h['cycle']:<8} | {s_name:<12} | {o_val:<8} | {str(h['switched']):<10} | {str(h['improved']):<10}")
        print("="*80)
        
        report = self.compute_stability_report()
        print(f"  🧠 [metrics] Stubbornness Index: {report['stubbornness_index']:.2f}")
        print(f"  🧠 [metrics] Recovery Latency:   {report['recovery_latency']} runs")
        print(f"  🧠 [metrics] Regret Persistence: {report['regret_persistence']} consecutive bad choices")
        print(f"  🧠 [metrics] Failure Escape Rate: {100*report['failure_escape_rate']:.1f}%")
