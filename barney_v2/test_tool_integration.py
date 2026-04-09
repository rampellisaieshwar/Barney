import sys
import os

# Add barney_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task

def run_tests():
    tasks = [
        "What are the latest iPhone 16 specs?",
        "Calculate the factorial of 10 using Python.",
        "Compare Python and Java for beginners."
    ]

    for i, task in enumerate(tasks):
        print(f"\n\n{'='*80}")
        print(f" 🧪 TEST CASE {i+1}: '{task}'")
        print(f"{'='*80}")
        
        result = run_task(task, mode="real")
        
        print(f"\n 🏁 TEST {i+1} COMPLETE")
        print(f"  🎯 STRATEGY: {result.get('suggested_strategy')}")
        print(f"  ⚖️ OUTCOME: {result.get('outcome_score')}")
        print(f"  🔧 TOOLS USED: {result.get('result', {}).get('tool_calls', 0)}")
        print(f"\n  Final Answer Summary: {str(result.get('result', {}).get('result'))[:200]}...")

if __name__ == "__main__":
    run_tests()
