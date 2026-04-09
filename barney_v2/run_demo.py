"""
Demo Runner for Python vs Java Comparison Task.
Verifies the cognitive stack's ability to handle complex, structured tasks.
"""

import sys
import os

# Add barney_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task, get_memory

def run_demo():
    print("\n" + "="*80)
    print(" 🧠 BARNEY v2 COGNITIVE EXECUTION: PYTHON VS JAVA 🧠 ")
    print("="*80)
    
    # Task from user
    task = "Compare Python and Java for beginners."
    
    # Contextual override (The user asked to prefer structured reasoning)
    # Our system alreay has a 'compare' heuristic for this.
    
    # Run the task in REAL mode
    # We want to see the LLM generate the plan, call tools, and produce an answer.
    result = run_task(task, mode="real", test_mode=False)
    
    print("\n" + "="*80)
    print(" 🏁 FINAL RESULT 🏁 ")
    print("="*80)
    print(f"TASK: {result['task']}")
    print(f"STRATEGY: {result['suggested_strategy']}")
    print(f"OUTCOME SCORE: {result['outcome_score']} (Eff. Signal: {result['effective_signal']})")
    print(f"COST: {result['cost']['steps']} steps, {result['cost']['tool_calls']} tool calls")
    print("\nANSWER:")
    print("-" * 40)
    print(result['result']['result'])
    print("-" * 40)


if __name__ == "__main__":
    run_demo()
