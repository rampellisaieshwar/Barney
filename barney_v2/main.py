"""
barney_v2 — Outcome Value & Learning Demo.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.loop import run_task, get_memory, evaluate_outcome
from core.strategy import select_strategy


def test_outcome_logic():
    print("\n--- TEST: Outcome Evaluation (Length/Structure/Overlap) ---")
    
    # 1. Short/Shallow
    res1 = evaluate_outcome("Who is the CEO of Apple?", "Tim Cook is ceo.")
    print(f"Short response (-1): {res1['score']} | {res1['reason']}")
    assert res1['score'] == -1
    
    # 2. Repeated/Reworded
    res2 = evaluate_outcome("Explain the impact of inflation in 2024", "The impact of inflation in 2024 is the major impact of inflation in the year 2024.")
    print(f"Repeated response (-1): {res2['score']} | {res2['reason']}")
    assert res2['score'] == -1
    
    # 3. Weak Structure (No markers)
    res3 = evaluate_outcome("Explain Python", "Python is a popular programming language used for web development and data science. It is easy to learn and versatile.")
    print(f"Weak structure (0): {res3['score']} | {res3['reason']}")
    assert res3['score'] == 0
    
    # 4. Informative (Markers)
    res4 = evaluate_outcome("Explain Python", "Python is a popular programming language because it has a simple syntax. For example, it uses indentation for block structure which helps reason about code.")
    print(f"Informative (+1): {res4['score']} | {res4['reason']}")
    assert res4['score'] == 1


def test_value_penalty():
    print("\n--- TEST: Outcome Value Penalty ---")
    
    # search: score=5, confidence=0.5, avg_outcome=-0.8 (Useless)
    # Penalty = max(0.4, 1 + -0.8) = 0.4
    # final_score = 5 * 0.4 = 2.0
    
    m1 = {
        "search": {"score": 5.0, "count": 10, "avg_steps": 2.0, "avg_tools": 1.0, "avg_outcome": -0.8}
    }
    res1 = select_strategy("Just find it", [], global_stats=m1)
    print(f"Score after penalty: {res1['confidence']:.2f}") # actually logging internal score would be better but let's see logs
    # Confidence is 5/10 = 0.5. Score should be penalized.


def test_value_protection():
    print("\n--- TEST: Value Protection (High Cost Allowed) ---")
    
    # validate: cost=8, confidence=0.9, score=9.0, outcome=+1.0 (VALUABLE)
    # search: cost=2, confidence=0.7, score=7.0, outcome=0.0
    # Regret is 6. Confidence < 1.0. 
    # BUT outcome is high (+1.0).
    # EXPECT: Protection rule allows validate.
    
    m2 = {
        "validate": {"score": 9.0, "count": 10, "avg_steps": 8.0, "avg_tools": 3.0, "avg_outcome": 1.0},
        "search": {"score": 7.0, "count": 10, "avg_steps": 2.0, "avg_tools": 1.0, "avg_outcome": 0.0}
    }
    res2 = select_strategy("Verify the details deep", [], global_stats=m2)
    print(f"Selected: {res2['suggested_strategy']} (Expect: validate due to high value protection)")
    assert res2['suggested_strategy'] == "validate"


def main():
    print("\n🧠 barney_v2 — Outcome Value Demo\n")
    memory = get_memory()
    memory.clear()

    # MISSION 8: High-Fidelity Valuation
    TASK_8 = "What is the capital of France? Give me a short answer."
    print(f"\n--- MISSION 8 [Shallow Outcome]: {TASK_8} ---")
    print("Agent should be penalized for short/shallow result.")
    run_task(TASK_8)
    
    # MISSION 9: Balanced Judgment
    TASK_9 = "Explain the difference between Python and Mojo in detail with examples."
    print(f"\n--- MISSION 9 [Valuable Outcome]: {TASK_9} ---")
    print("Agent should be rewarded for informative result.")
    run_task(TASK_9)

if __name__ == "__main__":
    test_outcome_logic()
    test_value_penalty()
    test_value_protection()
    main()
