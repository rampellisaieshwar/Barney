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

        # 1. Dynamic Economic Guardrails (Phase 35)
        # Instead of $0.002 magic number, use steps * cost_prediction
        budget_floor = SemanticEvaluator.get_dynamic_budget_floor(remaining_steps)
        if budget_remaining < budget_floor:
             print(f"  💸 [router] Dynamic Floor hit (Need ${budget_floor:.4f}, have ${budget_remaining:.4f}). Forcing FAST.")
             return MODEL_REGISTRY["llama-3.1-8b-instant"]["id"]

        # 2. Performance-Based Routing (Quality Yield)
        # We track how good the 'fast' model actually is in this domain.
        fast_quality = get_model_experience(task_type, "llama-3.1-8b-instant")
        strong_quality = get_model_experience(task_type, "llama-3.3-70b-versatile")
        
        # If the 'fast' model has a >90% quality yield for this task type, use it to save costs.
        if fast_quality > 0.9 and role == "strong" and complexity < 8:
             print(f"  🧠 [router] 8b Quality Yield ({fast_quality*100:.1f}%) is high for '{task_type}'. Optimizing.")
             return MODEL_REGISTRY["llama-3.1-8b-instant"]["id"]
             
        # If the 'fast' model is failing the quality floor (<60%), upsell to strong.
        if role == "fast" and fast_quality < 0.6 and strong_quality > 0.8:
             print(f"  📈 [router] 8b Quality Yield ({fast_quality*100:.1f}%) is sub-floor. Upselling to Strong.")
             return MODEL_REGISTRY["llama-3.3-70b-versatile"]["id"]

        # 3. Congestion/Pressure Awareness
        if role == "strong" and complexity < 7:
            pressure = get_throttle_pressure(MODEL_REGISTRY["llama-3.3-70b-versatile"]["id"])
            if pressure > 8:
                print(f"  🚦 [router] 70b pressure high ({pressure}/10). Shifting to fast tier.")
                return MODEL_REGISTRY["llama-3.1-8b-instant"]["id"]

        # 4. Standard Role-Based Selection
        if role == "strong" or complexity > 5:
            return MODEL_REGISTRY["llama-3.3-70b-versatile"]["id"]
            
        return MODEL_REGISTRY["llama-3.1-8b-instant"]["id"]

    @staticmethod
    def calculate_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates USD cost based on token usage."""
        model_meta = MODEL_REGISTRY.get(model_id)
        if not model_meta: return 0.0
        
        cost = (prompt_tokens * model_meta["cost_in"]) + (completion_tokens * model_meta["cost_out"])
        return round(cost, 6)
