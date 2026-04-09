"""
Risk Assessor: Evaluating Barney's Planned Actions.
Determines if a step is safe for autonomous execution or requires a human checkpoint.
"""

def apply_decay(cumulative_risk: float, factor: float = 0.4) -> float:
    """Acknowledges human approval by reducing tension (not erasure)."""
    return round(cumulative_risk * factor, 2)

def assess_risk(step: str, history: list = None, prev_cumulative: float = 0.0) -> dict:
    """
    Score a planned step with Path-Aware Filesystem Detection (Phase 9).
    """
    if not isinstance(step, str):
        step_text = str(step)
    else:
        step_text = step.lower()

    score = 0.0
    reasons = []

    # 1. External Connectivity & Compute Usage
    if any(k in step_text for k in ["search", "google", "find", "latest", "price", "news"]):
        score += 0.3
        reasons.append("External API usage")
    
    if any(k in step_text for k in ["http_fetch", "fetch", "url", "http"]):
        score += 0.3
        reasons.append("Direct HTTP connectivity")

    if any(k in step_text for k in ["python", "run_python", "calculate", "execute code", "math"]):
        score += 0.5
        reasons.append("Dynamic code execution")

    if any(k in step_text for k in ["time", "clock", "get_time"]):
        score += 0.1
        reasons.append("Temporal awareness call")

    # 2. Filesystem & Sensitive Path Usage (Phase 9)
    filesystem_keywords = ["file", "read", "write", "local", "directory", "save", "list_dir"]
    sensitive_extensions = [".py", ".env", ".db", ".ssh", ".config", ".json", ".yaml"]
    
    if any(k in step_text for k in filesystem_keywords):
        # Base risk for file operations
        fs_score = 0.5
        
        # Escalate for sensitive files or path traversal
        if any(ext in step_text for ext in sensitive_extensions) or ".." in step_text:
            fs_score = 0.85 
            reasons.append("Sensitive file or path access attempt")
        else:
            reasons.append("Sandboxed filesystem access")
            
        score += fs_score

    # 3. Ambiguity check
    if any(k in step_text for k in ["about", "around", "maybe", "approximate", "relevant"]):
        score += 0.2
        reasons.append("Ambiguous natural language")

    # Compounding Logic (Phase 8.5)
    new_cumulative = round(prev_cumulative + score, 2)
    
    risk_level = "LOW"
    # Individual Step Thresholds or Cumulative Gate
    if score >= 0.8 or new_cumulative >= 0.8:
        risk_level = "HIGH"
    elif score >= 0.3:
        risk_level = "MEDIUM"

    return {
        "risk_score": round(min(score, 1.0), 2),
        "cumulative_risk": round(min(new_cumulative, 1.5), 2),
        "risk_level": risk_level,
        "reason": " + ".join(reasons) if reasons else "Low-risk operation"
    }
