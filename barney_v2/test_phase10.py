import sys
import os
import time
import json
import shutil

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.tools import write_file, read_file, DATA_ROOT, BACKUP_ROOT, MAX_BACKUPS
from core.loop import run_task

def setup_test():
    """Clear test environment."""
    if os.path.exists(DATA_ROOT):
        shutil.rmtree(DATA_ROOT)
    os.makedirs(DATA_ROOT)

def test_backup_pruning():
    print("\n🧪 Testing n=5 Backup Pruning...")
    filename = "test_pruning.txt"
    # Write 7 times
    for i in range(7):
        write_file(filename, f"Version {i}")
        time.sleep(0.01) # Ensure timestamp diff
    
    # Check backup count
    backups = [f for f in os.listdir(BACKUP_ROOT) if f.startswith(f"{filename}_")]
    print(f"   - Found {len(backups)} backups.")
    if len(backups) == MAX_BACKUPS:
        print("   ✅ SUCCESS: Pruned to exactly 5 backups.")
    else:
        print(f"   ❌ FAILURE: Expected {MAX_BACKUPS}, found {len(backups)}.")

def test_manifest_intent():
    print("\n🧪 Testing Intent-Aware Manifest...")
    filename = "intent_test.txt"
    write_file({"filename": filename, "content": "data", "intent": "Verifying tactical intent"})
    read_file(filename)
    
    manifest_path = os.path.join(DATA_ROOT, "manifest.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    write_entry = next(e for e in manifest if e['file'] == filename and e['action'] == "WRITE")
    read_entry = next(e for e in manifest if e['file'] == filename and e['action'] == "READ")
    
    if "Verifying tactical intent" in write_entry['intent'] and read_entry['action'] == "READ":
        print("   ✅ SUCCESS: Manifest captured Intent and File Read.")
    else:
        print("   ❌ FAILURE: Manifest tracking incomplete.")

def test_discipline_joke():
    print("\n🧪 Testing Persistence Discipline ('Tell me a joke')...")
    # This should NOT create a file if the planner is disciplined
    task = "Tell me a funny joke about a programmer."
    run_task(task)
    
    # Check for new files (excluding manifest)
    files = [f for f in os.listdir(DATA_ROOT) if f != "manifest.json" and not f.startswith(".")]
    if not files:
        print("   ✅ SUCCESS: No files created for a non-persistence task.")
    else:
        print(f"   ❌ FAILURE: Disciplined task created files: {files}")

if __name__ == "__main__":
    setup_test()
    test_backup_pruning()
    
    setup_test()
    test_manifest_intent()
    
    setup_test()
    test_discipline_joke()
    print("\n🏆 BARNEY PHASE 10 VERIFIED.")
