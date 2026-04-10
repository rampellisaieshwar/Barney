"""
End-to-end test for the "No answer generated" fix.
Bypasses Redis/worker infrastructure and directly tests the LLM → Planner → Executor chain.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# --- Mock Redis to bypass infrastructure dependency ---
import types

_mock_store = {}

def _mock_check_throttle(*a, **kw): return False
def _mock_add_usage(*a, **kw): pass
def _mock_get_task(task_id):
    return _mock_store.get(task_id, {"status": "RUNNING", "metrics": {"total_tokens": 0, "total_cost": 0.0}, "budget_usd": 0.05})
def _mock_update_task(task_id, status, result=None, **kw):
    _mock_store[task_id] = {"task_id": task_id, "status": status, "result": result, "metrics": {"total_tokens": 0, "total_cost": 0.0}, "budget_usd": 0.05, "logs": [], "updated_at": 0}
def _mock_append_log(*a, **kw): pass
def _mock_record_exp(*a, **kw): pass
def _mock_enqueue(*a, **kw): pass
def _mock_noop(*a, **kw): return None
def _mock_false(*a, **kw): return False
def _mock_zero(*a, **kw): return 0

# Create mock redis_client module
mock_redis = types.ModuleType("redis_client")
mock_redis.check_llm_throttle = _mock_check_throttle
mock_redis.add_task_usage = _mock_add_usage
mock_redis.get_task = _mock_get_task
mock_redis.update_task = _mock_update_task
mock_redis.append_log = _mock_append_log
mock_redis.record_model_experience = _mock_record_exp
mock_redis.enqueue_task = _mock_enqueue
mock_redis.get_step_result = _mock_noop
mock_redis.acquire_step_lock = lambda *a, **kw: True
mock_redis.release_step_lock = _mock_false
mock_redis.save_step_result = _mock_noop
mock_redis.refresh_lock = _mock_false
mock_redis.get_active_high_cost_count = _mock_zero
mock_redis.change_active_high_cost_count = _mock_zero
mock_redis.get_throttle_pressure = _mock_zero
mock_redis.get_model_experience = lambda *a, **kw: 1.0
mock_redis.get_tool_result = _mock_noop
mock_redis.save_tool_result = _mock_noop
mock_redis.is_rate_limited = _mock_false
mock_redis.index_user_task = _mock_noop
mock_redis.get_user_history = lambda *a, **kw: []

sys.modules["redis_client"] = mock_redis

# Now import the actual code
from core.llm import call_llm
from core.loop import run_task

def test_llm_direct():
    """Test 1: Verify call_llm returns proper structure."""
    print("\n" + "="*60)
    print("TEST 1: Direct LLM Call")
    print("="*60)
    
    result = call_llm("What is 2+2? Give a brief answer.", role="fast")
    
    assert result is not None, "❌ call_llm returned None!"
    assert isinstance(result, dict), f"❌ call_llm returned {type(result)}, expected dict"
    assert "content" in result, f"❌ Missing 'content' key. Keys: {result.keys()}"
    assert len(result["content"].strip()) > 0, "❌ Content is empty!"
    
    print(f"\n✅ TEST 1 PASSED")
    print(f"   Content: {result['content'][:100]}...")
    print(f"   Model: {result.get('model')}")
    print(f"   Confidence: {result.get('confidence')}")
    return True

def test_full_pipeline():
    """Test 2: Full pipeline — the actual 'No answer generated' scenario."""
    print("\n" + "="*60)
    print("TEST 2: Full Pipeline (Explain black holes)")
    print("="*60)
    
    task = "Explain black holes in simple terms."
    task_id = "test-fix-001"
    _mock_update_task(task_id, "PENDING")
    
    result = run_task(task, task_id=task_id)
    
    print(f"\n--- Pipeline Result ---")
    print(f"Status: {result.get('status')}")
    
    result_data = result.get("result", {})
    final_answer = result_data.get("result", "") if isinstance(result_data, dict) else str(result_data)
    
    print(f"Answer length: {len(final_answer)}")
    print(f"Answer preview: {str(final_answer)[:200]}...")
    
    is_no_answer = final_answer == "No answer generated."
    if is_no_answer:
        print("\n❌ TEST 2 FAILED: Still getting 'No answer generated.'!")
        print(f"   state.result = {result.get('state', {}).get('result')}")
        print(f"   state.history_text = {str(result.get('state', {}).get('history_text', ''))[:200]}")
        return False
    else:
        print(f"\n✅ TEST 2 PASSED: Got actual content!")
        return True

if __name__ == "__main__":
    print("🧪 Running E2E Fix Verification\n")
    
    t1 = test_llm_direct()
    t2 = test_full_pipeline() if t1 else False
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Test 1 (LLM Direct): {'✅ PASS' if t1 else '❌ FAIL'}")
    print(f"  Test 2 (Full Pipeline): {'✅ PASS' if t2 else '❌ FAIL'}")
    
    if t1 and t2:
        print("\n🎉 All tests passed! The 'No answer generated' bug is FIXED.")
    else:
        print("\n⚠️ Some tests failed. Check output above for details.")
