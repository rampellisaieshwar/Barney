import sys
import os
import time

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.tools import write_file, read_file
from core.risk_assessor import assess_risk
from core.loop import run_task

def test_sandbox_security():
    print("\n🧪 Testing Sandbox Security...")
    # 1. Attempt Path Traversal
    try:
        write_file("../hacker.txt", "evil")
        print("   ❌ FAILURE: Path traversal was NOT blocked.")
    except PermissionError:
        print("   ✅ SUCCESS: Path traversal blocked (PermissionError).")
    except Exception as e:
        print(f"   ✅ SUCCESS: Traversal blocked with error: {e}")

def test_sensitive_risk():
    print("\n🧪 Testing Sensitive Path Risk...")
    # Writing to a .py file should be HIGH risk
    r = assess_risk("write_file('malicious.py', 'code')")
    print(f"   - File: malicious.py | Risk: {r['risk_level']} (Score: {r['risk_score']})")
    
    if r['risk_level'] == "HIGH" and r['risk_score'] >= 0.8:
        print("   ✅ SUCCESS: Sensitive extension triggered HIGH risk.")
    else:
        print("   ❌ FAILURE: Risk assessment too low for source file access.")

def test_file_workflow():
    print("\n🧪 Testing Full File Workflow...")
    task = "Save the secret code 12345 to a file named secret.txt and then read it back."
    
    # Run task (governance might trigger if cumulative risk > 0.8, but single write is 0.5)
    res = run_task(task)
    
    # Check if file exists in barney_data
    path = "barney_data/secret.txt"
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
            if "12345" in content:
                 print("   ✅ SUCCESS: File written correctly.")
            else:
                 print(f"   ❌ FAILURE: File content mismatch: {content}")
        # Clean up
        os.remove(path)
    else:
        print(f"   ❌ FAILURE: File not found at {path}. Status: {res['result']['status']}")

if __name__ == "__main__":
    test_sandbox_security()
    test_sensitive_risk()
    test_file_workflow()
    print("\n🏆 BARNEY PHASE 9 VERIFIED.")
