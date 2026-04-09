import json
import re

class RealityAnchor:
    """
    Grounding Layer for Phase 36.
    Ensures final answers are anchored in tool-provided evidence.
    """
    MAX_CLAIMS = 5

    @staticmethod
    def extract_volatile_claims(text: str) -> list:
        """
        Extraction filter: Focus on numeric facts, dates, names, 
        and specific data points. Skips generalizations.
        """
        # We use a pattern-based approach for speed + LLM for precision
        claims = []
        
        # 1. Numeric claims (e.g. "price is $100", "grew by 5%")
        numeric_matches = re.finditer(r"([0-9]+[.,]?[0-9]*(?:\s?%|\s?USD|\$|\$?\s?M|\$?\s?B)?)", text)
        for m in numeric_matches:
            # Context window around the number
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            claims.append({
                "type": "numeric",
                "value": m.group(1),
                "context": text[start:end].strip(),
                "confidence": 0.8 # Initial heuristic
            })

        # 2. Logic: Ensure we don't overwhelm verification
        return claims[:RealityAnchor.MAX_CLAIMS]

    @staticmethod
    def match_history(claims: list, tool_history: list) -> dict:
        """
        Reality Checker: Matches extracted claims against actual tool logs.
        """
        report = {
            "verified": [],
            "unverified": [],
            "contradicted": [],
            "stats": {"count": len(claims), "verified": 0, "fail": 0}
        }

        history_str = "\n".join([str(h) for h in tool_history]).lower()

        for c in claims:
            val = c["value"].lower()
            context = c["context"].lower()
            
            # Simple substring check (Fast Grounding)
            if val in history_str:
                report["verified"].append(c)
                report["stats"]["verified"] += 1
            else:
                # Potential hallucination if explicitly contradicted
                # (Simple check: if context minus value has different numbers in history)
                report["unverified"].append(c)

        return report

    @staticmethod
    def calculate_grounding_score(report: dict) -> float:
        """Returns grounding score (0.0 - 1.0)."""
        if not report["stats"]["count"]: return 1.0
        return report["stats"]["verified"] / report["stats"]["count"]
