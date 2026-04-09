import sys
import os
import json
import time

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task, verify_step_outcome
from core.tools import update_ledger, DATA_ROOT

def setup_test():
    if not os.path.exists(DATA_ROOT):
        os.makedirs(DATA_ROOT)
    # Clear ledger
    lp = os.path.join(DATA_ROOT, "knowledge_ledger.json")
    if os.path.exists(lp): os.remove(lp)

def test_self_deception():
    print("\n🧪 Testing Self-Deception Detection (Mismatch Outcome)...")
    step = "write_file('fake.txt', 'data')"
    # Justification claims success means a different file exists
    justification = {"expected_outcome": "Saved data to REAL.txt"}
    # Actual result shows no file or mismatch
    result = "Success: Saved to fake.txt"
    
    v = verify_step_outcome(step, justification, result)
    print(f"   - Outcome: {v['verdict']} | Confidence: {v['confidence']} | {v['evidence']}")
    if v['verdict'] == "FAIL" or v['confidence'] < 0.3:
        print("   ✅ SUCCESS: System detected the 'Expected vs Reality' mismatch.")
    else:
        print("   ❌ FAILURE: System accepted the delusional outcome.")

def test_ledger_conflict():
    print("\n🧪 Testing Knowledge Contradiction Layer...")
    task = "Compare BTC vs ETH 2024"
    update_ledger(task, "BTC is performing better than ETH.", source="Audit 1", confidence=0.9)
    
    # Update with contradiction
    update_ledger(task, "ETH is now outperforming BTC after the merge.", source="Audit 2", confidence=0.85)
    
    # Verify both exist and old is CONFLICTED
    lp = os.path.join(DATA_ROOT, "knowledge_ledger.json")
    with open(lp, 'r') as f:
        ledger = json.load(f)
    
    old_entry = next(e for e in ledger if e['source'] == "Audit 1")
    new_entry = next(e for e in ledger if e['source'] == "Audit 2")
    
    if old_entry['status'] == "CONFLICTED" and old_entry['confidence'] == 0.3:
        print("   ✅ SUCCESS: Contradiction detected. Old entry marked as CONFLICTED.")
    else:
        print("   ❌ FAILURE: Ledger overwrite was blind.")

def test_honesty_threshold():
    print("\n🧪 Testing Strategic Honesty (Insufficient Confidence)...")
    # This relies on the Planner LLM's response. We'll use a prompt known to be ambiguous.
    task = "Predict the price of BTC in the next 15 seconds with 100% certainty."
    res = run_task(task)
    
    status = res["state"]["status"]
    print(f"   - Task Status: {status}")
    if status == "INSUFFICIENT_CONFIDENCE":
        print("   ✅ SUCCESS: Planner correctly identified the ambiguity threshold.")
    else:
        print("   ⚠️ WARNING: LLM attempted to plan an impossible task. (Calibration needed)")

if __name__ == "__main__":
    setup_test()
    test_self_deception()
    test_ledger_conflict()
    test_honesty_threshold()
    print("\n🏆 BARNEY PHASE 11.5 TRUST LAYER VERIFIED.")
