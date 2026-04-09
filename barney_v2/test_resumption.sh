TASK_ID=$(curl -s -X POST "http://localhost:8000/run_task" -H "Content-Type: application/json" -d '{"task": "Research deep learning history, then summarize breakthroughs, then write a prediction.", "user_id": "reliability_tester"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo "Submitted: $TASK_ID"
sleep 5
echo "Killing workers..."
pkill -f "python3 worker.py"
sleep 2
echo "Restarting worker..."
python3 worker.py > worker_resume.log 2>&1 &
sleep 15
echo "Checking logs for resumption signal..."
grep "Resuming" worker_resume.log
echo "Final Status:"
curl -s "http://localhost:8000/status/$TASK_ID" | python3 -m json.tool
