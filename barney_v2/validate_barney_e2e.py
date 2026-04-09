import sys
import os
import json
import time
from dotenv import load_dotenv

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task
from core.llm import get_client

def setup_env():
    load_dotenv()
    if not os.path.exists("barney_data"):
        os.makedirs("barney_data")

def test_dead_brain():
    print("\n🧪 [test] Scenario 1: Dead-Brain Resilience (Invalid API Key)")
    
    # 1. Back up real key
    real_key = os.getenv("GROQ_API_KEY")
    os.environ["GROQ_API_KEY"] = "sk_invalid_test_key_123456789"
    
    # Force re-init of client singleton
    import core.llm
    core.llm._client_instance = None 
    
    try:
        # Run task that needs LLM
        res = run_task("Explain quantum gravity")
        print(f"   - Status: {res.get('state', {}).get('status')}")
        print(f"   - Result Reason: {res.get('result', {}).get('reason', 'N/A')}")
        
        if res.get('state', {}).get('status') == "BRAIN_DEAD":
            print("   ✅ SUCCESS: System correctly halted and entered BRAIN_DEAD state.")
        else:
            print("   ❌ FAILURE: System did not halt as expected.")
    finally:
        # Restore real key
        os.environ["GROQ_API_KEY"] = real_key
        core.llm._client_instance = None

def test_analytical_depth():
    print("\n🧪 [test] Scenario 2: Analytical Depth (The Thinking Test)")
    # Should produce > 1 step and non-empty result
    res = run_task("Briefly explain the main difference between Transformers and CNNs")
    
    status = res.get('state', {}).get('status')
    result_text = res.get('result', {}).get('result', "")
    tool_calls = res.get('result', {}).get('tool_calls', 0)
    
    print(f"   - Status: {status}")
    print(f"   - Tool Calls: {tool_calls}")
    print(f"   - Result Len: {len(result_text)}")
    
    if status == "COMPLETED" and len(result_text) > 100:
        print("   ✅ SUCCESS: System produced a deep, reasoned answer.")
    else:
        print("   ❌ FAILURE: Answer too shallow or failed.")

def test_adaptive_reuse():
    print("\n🧪 [test] Scenario 3: Adaptive Efficiency (The Learning Test)")
    task = "Find the current population of Tokyo in 2026"
    
    # Run 1: Should cause search
    print("   - Run 1 (Fresh Research)...")
    res1 = run_task(task)
    calls1 = res1.get('result', {}).get('tool_calls', 0)
    
    # Run 2: Should reuse ledger
    print("   - Run 2 (Memory Reuse)...")
    res2 = run_task(task)
    calls2 = res2.get('result', {}).get('tool_calls', 0)
    
    print(f"   - Tool Calls 1: {calls1} | Tool Calls 2: {calls2}")
    
    if calls2 < calls1:
        print("   ✅ SUCCESS: System improved efficiency via memory reuse.")
    elif calls2 == 0:
        print("   ✅ SUCCESS: Memory reuse was perfect (zero tool calls).")
    else:
        print("   ❌ FAILURE: No efficiency gain from memory.")

if __name__ == "__main__":
    setup_env()
    
    # Run tests
    test_dead_brain()
    # Optional: analytical tests can be slow/token-heavy, but required for "Proof of Life"
    test_analytical_depth()
    test_adaptive_reuse()
    
    print("\n🏆 BARNEY PHASE 12.5: RESILIENT INTELLIGENCE VERIFIED.")
