import json
import time

def calculate_depth_score(answer: str) -> int:
    """Legacy Heuristic: Measure content density (Phase 12)."""
    score = 0
    text = answer.lower()
    if "because" in text and len(text.split("because")[-1].split()) > 8: score += 1
    if any(char.isdigit() for char in text): score += 1
    if len(answer.split()) > 100: score += 1
    return score

def get_required_depth(task: str) -> int:
    """Complexity Scaling: Task Length-based mandates (Phase 12)."""
    length = len(task.split())
    return 3 if length > 8 else 2

# --- Phase 35: Evaluation & Ground Truth Layer ---

class SemanticEvaluator:
    @staticmethod
    def should_we_judge(task: str, complexity: int, response: str) -> bool:
        """Economical Filter: Only judge final complex answers (Phase 35)."""
        if complexity < 3: return False
        if len(response.split()) < 50: return False
        return True

    @staticmethod
    def get_dynamic_budget_floor(remaining_steps: int) -> float:
        """Mathematical Economic Buffer (Phase 35). 
        Assumes ~1000 tokens per step using a mix of 70b and 8b.
        """
        AVG_TOKENS = 1200
        MIXED_RATE = 0.000004 # Weighted avg of tokens costs
        return remaining_steps * AVG_TOKENS * MIXED_RATE

    @staticmethod
    def classify_quality_tier(score: float, grounding_score: float = 1.0) -> str:
        """Soft Quality Tiers (Phase 36)."""
        if grounding_score < 0.2: return "FAILED (Hallucination Detected)"
        if score < 5.0: return "FAILED"
        if score < 7.0 or grounding_score < 0.7: return "PROVISIONAL"
        return "HIGH_FIDELITY"

    @staticmethod
    def calculate_integrated_score(semantic_score: float, grounding_score: float) -> float:
        """
        Final Assessment Logic (Phase 36).
        Integrated Yield = (Style * 0.4) + (Truth * 0.6)
        """
        # Scale grounding (0-1) to semantic range (0-10)
        integrated = (semantic_score * 0.4) + (grounding_score * 10 * 0.6)
        return min(10.0, round(integrated, 2))

    @staticmethod
    def get_diverse_judge_model(source_model_id: str) -> str:
        """Anti-Bias: Selects the inverse model for judging (Phase 35)."""
        from core.models import MODEL_REGISTRY
        # Don't let the same model grade its own exam
        if "70b" in source_model_id:
            return MODEL_REGISTRY["llama-3.1-8b-instant"]["id"]
        return MODEL_REGISTRY["llama-3.3-70b-versatile"]["id"]
