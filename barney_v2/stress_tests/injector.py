"""
Injector: Utility for seeding memory with adversarial history.
(Stress Test Layer #8)
"""

from core.loop import get_memory


def inject_strategy(strategy: str, count: int, outcome_score: int = -1, success: bool = True):
    """
    Seed memory with specific strategy history.
    Used to poison confidence or simulate high-value successes.
    """
    memory = get_memory()
    print(f"  💉 [injector] Injecting {count} entries for '{strategy}' (Outcome: {outcome_score}, Success: {success})")
    
    for _ in range(count):
        # Create an execution insight
        insight = {
            "type": "tool",
            "task_type": "general",
            "condition": "general",
            "success": success,
            "lesson": f"Injected history for {strategy}",
            "improvement": "None",
            "timestamp": memory.count() + 1,
            "original_task": f"Pressure Test Task for {strategy}",
            "strategy_trace": [strategy],
            "cost": {"steps": 2, "tool_calls": 1},
            "outcome_score": outcome_score
        }
        memory.add(insight)
        
        # Also add a plan insight to maintain schema expectations
        plan_insight = {
            "type": "plan",
            "task": f"Pressure Test Task for {strategy}",
            "task_type": "general",
            "condition": "general",
            "strategy_trace": [strategy],
            "plan": [f"Execute {strategy}"],
            "score": 1 if success else -1,
            "success": success,
            "timestamp": memory.count() + 1,
            "cost": {"steps": 1, "tool_calls": 0},
            "outcome_score": outcome_score
        }
        memory.add(plan_insight)

    print(f"  💉 [injector] Injection complete. Memory size: {memory.count()}")
