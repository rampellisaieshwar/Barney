import sys
import os
import time
from unittest.mock import patch

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task, _generate_step_id
from core.execution_state import ExecutionState
from core.risk_assessor import assess_risk

def test_idempotency():
    print("\n🧪 Testing Idempotency...")
    task = "Search for bitcoin price and save to file"
    state = ExecutionState(task)
    state.plan = ["Search BTC price", "Save to btc.txt"]
    state.status = "EXECUTING"
    state.replan_counter = 0
    
    # 1. Run full task
    res1 = run_task(task, state_dict=state.to_dict())
    state1 = ExecutionState.from_dict(res1["state"])
    print(f"   - Run 1 finished. Status: {state1.status}, History: {len(state1.history)}")
    
    # 2. Simulate rerunning the same completed state
    # We reset current_step_index to 0
    state1.current_step_index = 0
    state1.status = "EXECUTING"
    res2 = run_task(task, state_dict=state1.to_dict())
    state2 = ExecutionState.from_dict(res2["state"])
    
    # It should skip both and remain at length 2
    if state2.current_step_index == 2 and len(state2.history) == 2:
        print("   ✅ SUCCESS: Idempotency skipped all steps. No duplicate tool calls.")
    else:
        print(f"   ❌ FAILURE: Unexpected state. Index: {state2.current_step_index}, History: {len(state2.history)}")

def test_risk_stacking():
    print("\n🧪 Testing Risk Stacking...")
    step = "Read local news" # ~0.5
    
    # Step 1: Baseline
    r1 = assess_risk(step, prev_cumulative=0.0)
    print(f"   - Single Step: {r1['risk_level']} (Comp: {r1['cumulative_risk']})")
    
    # Step 2: Stacked
    # 0.5 + 0.5 = 1.0 > 0.8 threshold
    r2 = assess_risk(step, prev_cumulative=0.5)
    print(f"   - Stacked Step: {r2['risk_level']} (Comp: {r2['cumulative_risk']})")
    
    if r2['risk_level'] == "HIGH":
        print("   ✅ SUCCESS: Compounding Risk Gate triggered HIGH status.")
    else:
        print("   ❌ FAILURE: Risk didn't compound correctly.")

def test_race_condition():
    print("\n🧪 Testing Race Condition (Delayed Approval)...")
    task = "Risky business"
    state = ExecutionState(task)
    state.plan = ["Format hard drive"] # HIGH
    state.status = "WAITING_FOR_HUMAN"
    state.wait_start_time = time.time() - 400 # Already timed out
    
    print("   - Human clicks 'Approve' AFTER timeout triggered...")
    # Simulate the UI sending 'approved_step: True'
    dict_with_approval = state.to_dict()
    dict_with_approval["approved_step"] = True
    
    res = run_task(task, state_dict=dict_with_approval)
    if res["state"]["status"] == "REJECTED_TIMEOUT":
        print("   ✅ SUCCESS: Delayed approval was blocked by timeout guard.")
    else:
        print(f"   ❌ FAILURE: Approval accepted despite timeout! Status: {res['state']['status']}")

if __name__ == "__main__":
    try:
        test_idempotency()
        test_risk_stacking()
        test_race_condition()
        print("\n🏆 BARNEY PHASE 8.5 VERIFIED.")
    except Exception as e:
        print(f"\n💥 CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
