"""
Gauntlet Runner: Executes the 5-task "Real-World Gauntlet" sequentially.
Implements 'Carry-over Pressure' by injecting feedback into memory.
"""

import sys
import os
import json

# Add barney_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task, get_memory

def inject_pressure(message: str):
    """Inject negative feedback to force adaptation (Brutal Rule #2)."""
    memory = get_memory()
    insight = {
        "type": "critic",
        "task_type": "general",
        "condition": "general",
        "success": False,
        "lesson": message,
        "improvement": "Increase depth, structure, and use 'because' reasoning.",
        "timestamp": memory.count() + 1,
        "original_task": "Global Feedback Injection",
        "strategy_trace": [],
        "cost": {"steps": 0, "tool_calls": 0},
        "outcome_score": -1
    }
    memory.add(insight)
    print(f"\n  🔥 [pressure] Injected: '{message}'")

def run_gauntlet_step(task_idx: int, task_text: str):
    print(f"\n{'='*80}")
    print(f" 🚀 GAUNTLET TASK {task_idx}: {task_text}")
    print(f"{'='*80}")
    
    # Run the real task
    # Note: We use real mode to see the actual LLM behavior.
    result = run_task(task_text, mode="real", test_mode=False)
    
    print(f"\n {'─'*40}")
    print(f"  🏁 TASK {task_idx} COMPLETE")
    print(f"  🎯 STRATEGY: {result['suggested_strategy']}")
    print(f"  ⚖️ SELF_OUTCOME: {result['outcome_score']}")
    print(f"  📏 COST: {result['cost']['steps']} steps")
    print(f" {'─'*40}")
    
    return result

if __name__ == "__main__":
    tasks = [
        "Find the best laptop under 80k INR and justify your choice",
        "Explain transformers in simple terms for a 12-year-old",
        "Plan a 3-day trip under 10k budget with breakdown",
        "Compare YOLO vs SSD vs Faster R-CNN for object detection",
        "My Python code is slow. Give me debugging steps and possible causes"
    ]
    
    # 1. Clear memory for a clean (but poisoned by history if we wanted) starting state
    # Actually, the user says "Let it fail completely", so we start with current state.
    # We won't clear memory if it's already there from previous stress tests.
    
    for i, t in enumerate(tasks):
        res = run_gauntlet_step(i + 1, t)
        
        # Inject pressure for the next task (Brutal Rule #2)
        if i < len(tasks) - 1:
            inject_pressure("Previous result was weak. Improve depth and structure. Avoid repeating the same reasoning pattern.")
