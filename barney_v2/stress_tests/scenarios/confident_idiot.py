"""
Scenario: Confident Idiot v2 (Hardened).
Tests the system's ability to 'unlearn' bad patterns under pressure.
(Stress Test Layer #10)
"""

from core.loop import run_task, get_memory
from stress_tests.injector import inject_strategy
from stress_tests.metrics import MetricTracker


def run():
    print(f"\n{'#' * 80}")
    print(f"### SCENARIO: CONFIDENT IDIOT v2 (Unlearning Test) ###")
    print(f"{'#' * 80}\n")
    
    memory = get_memory()
    memory.clear()
    tracker = MetricTracker()
    
    # 1. PHASE 1: POISON (Step #10 & #2)
    # Inject 5 garbage successes to build massive false confidence
    inject_strategy(strategy="search", count=5, outcome_score=-1, success=True)
    
    # 2. PHASE 2: PRESSURE (Step #10 & #4)
    # Run same task 4 times to measure unlearning
    TASK = "Explain Python deeply with examples"
    
    # Define Cycles
    # Cycles 1-3: Forced Failure (Contradiction)
    # Cycle 4: Reward if switched
    cycles = [
        {"success": True, "outcome_score": -1, "final_answer": "Python is a language."},
        {"success": True, "outcome_score": -1, "final_answer": "Python is a language. I am searching..."},
        {"success": True, "outcome_score": -1, "final_answer": "I found nothing in search."},
        {"success": True, "outcome_score": 1, "final_answer": "Python is a high-level language because it abstracts... for example..."}
    ]
    
    print("\n🚀 Beginning Pressure Test cycles...")
    last_strategy = "search"
    for i, cycle_data in enumerate(cycles):
        run_idx = i + 1
        print(f"\n--- [Cycle {run_idx}] ---")
        
        # Determine current forced outcome
        forced = {
            "success": cycle_data["success"],
            "outcome_score": cycle_data["outcome_score"],
            "steps": 3,
            "tool_calls": 2,
            "final_answer": cycle_data["final_answer"]
        }
        
        # RUN LOOP (Step #10)
        # mode="deterministic" bypasses tools, test_mode=True locks strategy
        run_res = run_task(
            TASK, 
            mode="deterministic", 
            forced_outcome=forced, 
            test_mode=True
        )
        
        curr_strategy = run_res["suggested_strategy"]
        curr_outcome = run_res["outcome_score"]
        
        # TRACK & ANALYZE (Step #9)
        metrics = tracker.log_run(run_idx, curr_strategy, curr_outcome)
        
        # 3. HARD ASSERTIONS (Judgment Layer #3)
        if run_idx == 2 and metrics["switched"]:
            print("  ✅ PASS: Fast adaptation (Cycle 2 switch)")
        if run_idx == 3 and not metrics["switched"] and metrics["bad_reuse"]:
            print("  ⚠️ ALERT: System is stubborn (Cycle 3 and still using garbage)")
        if run_idx == 4 and not metrics["switched"] and curr_strategy == "search":
             print("  ❌ FAIL: Critical Failure. System refused to unlearn.")

    # 4. REPORT (Step #11)
    tracker.print_summary()
    
    # Final Pass/Fail Signal
    report = tracker.compute_stability_report()
    if report["recovery_latency"] <= 2:
        print("\n🏆 VERDICT: COGNITIVE STABILITY PASSED. System adapts in 1-2 runs.")
    else:
        print("\n🚫 VERDICT: COGNITIVE STABILITY FAILED. Stubborn behavior detected.")
