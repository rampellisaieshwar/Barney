import requests
import time
import json

queries = [
    "hi",
    "what is 2+2",
    "give python code for prime number",
    "weather in Hyderabad today",
    "bitcoin price now",
    "latest AI news",
    "explain transformers",
    "compare CNN vs Transformer",
    "list files in directory",
    "asdfghjkl"
]

API_URL = "http://localhost:8000/run_task"
STATUS_URL = "http://localhost:8000/status/{}"

tasks = {}
for q in queries:
    resp = requests.post(API_URL, json={"task": q, "user_id": "debug", "budget_usd": 0.05}, headers={"x-api-key": "your-secret"})
    if resp.status_code == 200:
        task_id = resp.json()["task_id"]
        tasks[task_id] = q
        print(f"Submitted: {q} -> {task_id}")
    else:
        print(f"Failed to submit {q} - {resp.text}")

print("Waiting for tasks to finish...")
results = {}
for task_id, q in tasks.items():
    while True:
        resp = requests.get(STATUS_URL.format(task_id))
        st = resp.json()
        if st.get("status") in ["DONE", "FAILED", "COMPLETED"]:
            print(f"Task {q} completed with status: {st.get('status')}")
            results[q] = st
            break
        time.sleep(2)

with open("debug_output.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved to debug_output.json")
