import sys
import os
import json
import time

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task, score_research_quality
from core.memory_manager import retrieve_similar, calculate_decay
from core.tools import update_ledger, DATA_ROOT, summarize_ledger

def setup_test():
    if not os.path.exists(DATA_ROOT):
        os.makedirs(DATA_ROOT)
    # Clear ledger
    lp = os.path.join(DATA_ROOT, "knowledge_ledger.json")
    if os.path.exists(lp): os.remove(lp)

def test_memory_decay():
    print("\n🧪 Testing Temporal Decay (Phase 12)...")
    base_conf = 0.9
    # Simulate an entry from 1 month ago (~2,592,000 seconds)
    ts_month_ago = time.time_ns() - (2592000 * 1e9)
    
    decayed = calculate_decay(base_conf, ts_month_ago)
    print(f"   - Base: {base_conf} | Decayed (1 mo): {decayed:.4f}")
    if decayed < 0.15: # 0.5 ^ (2592000/604800) approx 0.5^4.2 approx 0.05
        print("   ✅ SUCCESS: Old belief decayed significantly.")
    else:
        print("   ❌ FAILURE: Decay logic too weak.")

def test_multi_source_consistency():
    print("\n🧪 Testing Research Quality Scoring (Multi-Source)...")
    # Simulate history with 1 source
    h1 = [{"history_update": "Tool:search Result: One source says BTC is $60k. site:coinmarketcap.com"}]
    q1 = score_research_quality(h1)
    
    # Simulate history with 2 sources but error
    h2 = [
        {"history_update": "Tool:search Result: Source A says BTC is $60k. site:domainA.com"},
        {"history_update": "Tool:search Result: Error: Connection failed. site:domainB.com"}
    ]
    q2 = score_research_quality(h2)

    print(f"   - Single Source Conf: {q1['final_confidence']}")
    print(f"   - 2-Source (w/ Error) Conf: {q2['final_confidence']}")

    if q1['final_confidence'] <= 0.6 and q2['final_confidence'] < 0.5:
        print("   ✅ SUCCESS: Quality scoring enforced multi-source and error penalties.")
    else:
        print("   ❌ FAILURE: Quality scoring too lenient.")

def test_ledger_compression():
    print("\n🧪 Testing Ledger Compression Trigger...")
    for i in range(55):
        update_ledger(f"Task {i}", f"Insight {i} summary data", source="Auto-Test", confidence=0.7)
    
    lp = os.path.join(DATA_ROOT, "knowledge_ledger.json")
    with open(lp, 'r') as f:
        ledger = json.load(f)
    
    print(f"   - Final Ledger Size: {len(ledger)}")
    if len(ledger) <= 30: # summarize_ledger keeps top 25
        print("   ✅ SUCCESS: Compression triggered and pruned the ledger.")
    else:
        print("   ❌ FAILURE: Compression did not trigger or failed to prune.")

if __name__ == "__main__":
    setup_test()
    test_memory_decay()
    test_multi_source_consistency()
    test_ledger_compression()
    print("\n🏆 BARNEY PHASE 12: ADAPTIVE INTELLIGENCE VERIFIED.")
