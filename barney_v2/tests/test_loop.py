"""
Tests for the barney_v2 core loop with real execution.

Verifies:
  1. A task produces a valid result with insight stored.
  2. Running the same task again retrieves prior memory.
"""

import sys
import os

# Ensure barney_v2 is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.loop import run_task, get_memory


def test_first_run_stores_insight():
    """First run should execute, produce insight, and store it."""
    memory = get_memory()
    memory.clear()

    output = run_task("search python tutorials")

    # Insight should be stored
    assert output["memory_size"] == 1, f"Expected 1 insight in memory, got: {output['memory_size']}"

    # No prior insights on first run
    assert output["prior_insights"] == [], f"Expected no prior insights, got: {output['prior_insights']}"

    # Insight should be well-formed
    insight = output["insight"]
    assert insight["task"] == "search python tutorials"
    assert isinstance(insight["success"], bool)
    assert "lesson" in insight
    assert "improvement" in insight

    # Result should have come from real execution
    result = output["result"]
    assert "task" in result
    assert "steps" in result
    assert "result" in result
    assert "status" in result

    print("✅ test_first_run_stores_insight PASSED")


def test_second_run_retrieves_memory():
    """Second run of the same task should find prior insights."""
    memory = get_memory()
    memory.clear()

    # Run 1
    output1 = run_task("search python tutorials")
    assert output1["prior_insights"] == [], "First run should have no prior insights"

    # Run 2 — same task
    output2 = run_task("search python tutorials")

    # Should have retrieved the insight from run 1
    assert len(output2["prior_insights"]) == 1, (
        f"Expected 1 prior insight, got: {len(output2['prior_insights'])}"
    )
    assert output2["prior_insights"][0]["task"] == "search python tutorials"

    # Memory should now have 2 insights total
    assert output2["memory_size"] == 2, f"Expected 2 insights, got: {output2['memory_size']}"

    print("✅ test_second_run_retrieves_memory PASSED")


if __name__ == "__main__":
    test_first_run_stores_insight()
    test_second_run_retrieves_memory()
    print("\n🎉 ALL TESTS PASSED")
