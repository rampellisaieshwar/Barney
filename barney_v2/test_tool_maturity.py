import sys
import os

# Add barney_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task

def run_tests():
    scenarios = [
        {"task": "What are the latest iPhone 16 specs?", "expect": "search triggered"},
        {"task": "Calculate 2+2", "expect": "zero tools (basic math)"},
        {"task": "Compare Python vs Java for beginners", "expect": "zero/low tools (reasoning)"},
        {"task": "What is the current weather in Hyderabad?", "expect": "search triggered"}
    ]

    for i, meta in enumerate(scenarios):
        task = meta["task"]
        print(f"\n\n{'='*80}")
        print(f" 🧪 MATURITY TEST {i+1}: '{task}'")
        print(f" 🎯 EXPECTATION: {meta['expect']}")
        print(f"{'='*80}")
        
        result = run_task(task, mode="real")
        
        print(f"\n 🏁 MATURITY {i+1} COMPLETE")
        print(f"  🔧 TOOLS USED: {result.get('result', {}).get('tool_calls', 0)}")
        print(f"  ⚖️ EFFECTIVE SIGNAL: {result.get('effective_signal')}")
        print(f"  ⚠️ REPEATED TOOL: {result.get('result', {}).get('repeated_tool', False)}")

if __name__ == "__main__":
    run_tests()
