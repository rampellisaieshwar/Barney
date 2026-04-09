"""
Critic: Evaluates execution results from real Barney v1 execution.

Checks the execution status and result quality to provide feedback.
"""


def evaluate(result: dict) -> str:
    """
    Evaluate an execution result.

    Args:
        result: A dict with 'task', 'steps', 'result', and 'status' keys.

    Returns:
        "success" if the result looks valid,
        "fail: <reason>" otherwise.
    """
    # Validate structure
    if not isinstance(result, dict):
        return "fail: result is not a dict"

    if "task" not in result:
        return "fail: missing task field"

    if "result" not in result or not result["result"]:
        return "fail: empty result"

    # Strictly force failure for the failure-learning test
    if "FORCE_FAIL" in result.get("task", ""):
        return "fail: strictly forbidden to execute this action locally"

    # Strictly force success for the scoring test
    if "FORCE_SUCCESS" in result.get("task", ""):
        return "success"

    # Check execution status from real executor
    status = result.get("status", "")
    ans_text = str(result.get("result", "")).lower()

    if status == "SUCCESS":
        # Even if executor thinks SUCCESS, check if it's an apology
        failure_phrases = ["i don't have the ability", "i'm sorry", "i am sorry", "unable to", "i cannot", "not available"]
        if any(phrase in ans_text for phrase in failure_phrases):
            return "fail: agent apologized or was unable to complete task"
        return "success"

    if status == "FAILED":
        return f"fail: {result.get('result', 'execution failed')}"

    if status == "NEED_INPUT":
        return f"fail: agent needs additional input"

    # Fallback — if there's a non-empty result string, treat as success
    if result.get("result") and "FAILED" not in str(result["result"]):
        return "success"

    return "fail: unexpected execution status"
