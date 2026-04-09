"""
Insight Engine: The learning brain of Barney v2.

Extracts atomized, actionable lessons and tracks cost + value metrics.
"""

import json
import re


def get_task_type(task: str) -> str:
    """Classify task based on keywords."""
    task = task.lower()
    if any(k in task for k in ["search", "find", "google", "research", "browse"]):
        return "web"
    if any(k in task for k in ["calculate", "math", "sum", "compute"]):
        return "compute"
    if any(k in task for k in ["file", "read", "local", "write"]):
        return "file"
    return "general"


def get_task_condition(task: str) -> str:
    """Identify environmental constraints."""
    task = task.lower()
    if "latest" in task or "news" in task:
        return "freshness"
    if "private" in task or "password" in task:
        return "privacy"
    return "general"


def extract_intent(step: str) -> str:
    """Identify the core reasoning intent of a single step."""
    if not isinstance(step, str):
        # Resilience: Handle ints, dicts or other objects returned by some LLMs
        if isinstance(step, dict):
            extracted = step.get("text") or step.get("description") or step.get("step") or str(step)
            step = str(extracted)
        else:
            step = str(step)
            
    step = step.lower().strip()
    words = step.split()
    if not words: return None
    
    first = words[0]
    if first in ["search", "find", "google", "retrieve", "gather", "research"]:
        return "search"
    if first in ["compare", "evaluate", "analyze", "contrast"]:
        return "compare"
    if first in ["summarize", "list", "extract", "shortlist"]:
        return "summarize"
    if first in ["rank", "order", "prioritize"]:
        return "rank"
    if first in ["validate", "check", "verify", "why"]:
        return "validate"
    return None


def extract_reason_trace(plan: list[str]) -> list[str]:
    """Reasoning Memory: Map a plan to a sequence of unique intents (Phase #4A)."""
    trace = []
    if not plan: return trace
    for step in plan:
        intent = extract_intent(step)
        if intent and intent not in trace:
            trace.append(intent)
    return trace


def extract_strategy_trace(plan: list) -> list:
    """Legacy: Map a plan of strings into a sequence of रीजनिंग intents."""
    return extract_reason_trace(plan)


def extract_insight(task: str, steps: list, result: str, feedback: str, timestamp: int, 
                    plan: list = None, cost: dict = None, outcome_score: int = 0) -> dict:
    """
    Analyze the trace and feedback to create a structured insight.
    Now tracks cost and outcome valuation.
    """
    success = feedback.strip().lower() == "success"
    task_type = get_task_type(task)
    condition = get_task_condition(task)
    
    # 1. Lesson extraction
    if success:
        lesson = f"Task '{task_type}' succeeded with tool(s)."
        improvement = "Maintain approach."
    else:
        lesson = f"Task '{task_type}' failed."
        improvement = "Pivot approach."

    # 2. Reasoning Trace (New: Reasoning Memory Phase #4A)
    reason_trace = extract_reason_trace(plan) if plan else []
    
    # 3. Decision Metrics (Judgment Layer: Cost + Value)
    cost_data = cost if cost else {"steps": 0, "tool_calls": 0}

    return {
        "task": task,
        "task_type": task_type,
        "condition": condition,
        "success": success,
        "lesson": lesson,
        "improvement": improvement,
        "timestamp": timestamp,
        "original_task": task,
        "strategy_trace": reason_trace,
        "reason_trace": reason_trace,
        "cost": cost_data,
        "outcome_score": outcome_score # Value metric
    }
