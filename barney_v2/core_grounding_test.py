import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from core.loop import run_task

def test_grounding():
    queries = [
        "latest AI news",
        "weather today in Hyderabad",
        "who won yesterday IPL match",
        "Analyze the impact of AI on job markets"
    ]
    
    print(f"🚀 [test] Starting Grounding-First Diagnosis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for q in queries:
        print(f"\n--- TESTING QUERY: {q} ---")
        res = run_task(q)
        
        print(f"  ✅ Status: {res.get('status')}")
        print(f"  📝 Answer: {res.get('answer', 'NO ANSWER')[:200]}...")
        print(f"  🔧 Tools Used: {res.get('tools_used')}")
        
        if res.get('status') == 'DONE' and res.get('answer'):
             print(f"  🌟 Result Quality: SUCCESS")
        else:
             print(f"  🚨 Result Quality: FAILED")

if __name__ == "__main__":
    test_grounding()
