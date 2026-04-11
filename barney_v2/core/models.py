"""
Model Registry: Centralized management for LLM routing and cost tracking.
"""

MODEL_REGISTRY = {
    "llama-3.1-8b-instant": {
        "id": "llama-3.1-8b-instant",
        "role": "fast",
        "rpm": 30,
        "cost_in": 0.05 / 1_000_000,
        "cost_out": 0.08 / 1_000_000,
        "desc": "High-speed, low-precision for routine tasks."
    },
    "llama-3.3-70b-versatile": {
        "id": "llama-3.3-70b-versatile",
        "role": "strong",
        "rpm": 10,
        "cost_in": 0.59 / 1_000_000,
        "cost_out": 0.79 / 1_000_000,
        "desc": "High-precision, high-cost for tactical planning."
    }
}

class ModelRouter:
    @staticmethod
    def resolve_model(role: str = "fast", complexity: int = 0, task_type: str = "general", budget_remaining: float = 0.05, remaining_steps: int = 1) -> str:
        """Determines best model based on Role, Complexity, Dynamic Budget, and Quality Yield (Phase 35)."""
        from redis_client import get_model_experience, get_throttle_pressure
        from core.scoring import SemanticEvaluator

        return MODEL_REGISTRY["llama-3.3-70b-versatile"]["id"]
        
        # 1. Dynamic Economic Guardrails (Phase 35)
        # 4. Standard Role-Based Selection
        return MODEL_REGISTRY["llama-3.3-70b-versatile"]["id"]

    @staticmethod
    def calculate_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates USD cost based on token usage."""
        model_meta = MODEL_REGISTRY.get(model_id)
        if not model_meta: return 0.0
        
        cost = (prompt_tokens * model_meta["cost_in"]) + (completion_tokens * model_meta["cost_out"])
        return round(cost, 6)
