# Barney VM Cheat Sheet

## SSH Into VM
```bash
ssh -i ~/Downloads/barney-vm_key.pem azureuser@20.40.60.199
```

---

## Check Status
```bash
# Are services running?
sudo systemctl status barney-worker barney-api --no-pager

# Is worker running?
ps aux | grep worker.py | grep -v grep

# Check logs
tail -50 ~/Barney/worker.log
tail -50 ~/Barney/api.log
```

---

## Start Services
```bash
sudo systemctl start barney-worker
sudo systemctl start barney-api
```

## Stop Services
```bash
sudo systemctl stop barney-worker
sudo systemctl stop barney-api
```

## Restart Services
```bash
sudo systemctl restart barney-worker
sudo systemctl restart barney-api
```

## Restart Everything (nuclear option)
```bash
sudo pkill -f worker.py
sudo pkill -f uvicorn
sleep 3
sudo systemctl restart barney-worker
sudo systemctl restart barney-api
```

---

## Deploy New Code
```bash
cd ~/Barney
git pull origin main
sudo systemctl restart barney-worker
sudo systemctl restart barney-api
```

---

## Turn Agent Mode ON/OFF
```bash
# ON
curl -X POST http://localhost:8000/agent_mode/toggle \
  -H "x-api-key: your-secret" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "default", "enabled": true}'

# OFF
curl -X POST http://localhost:8000/agent_mode/toggle \
  -H "x-api-key: your-secret" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "default", "enabled": false}'

# Check status
curl "http://localhost:8000/agent_mode/status?user_id=default" \
  -H "x-api-key: your-secret"
```

---

## Redis Quick Checks
```bash
# Open Redis CLI
redis-cli

# Check all keys
KEYS *

# Check agent mode
GET agent_mode:default

# Check credential vault
KEYS agent_cred:*

# Clear a stuck task
DEL <task_id>
```

---

## Live Log Watching
```bash
# Watch worker logs live
tail -f ~/Barney/worker.log

# Watch via systemd
sudo journalctl -u barney-worker -f
sudo journalctl -u barney-api -f
```

---

## If Worker Is Not Picking Up Tasks
```bash
# 1. Check it's running
ps aux | grep worker.py | grep -v grep

# 2. If not running, start it
sudo systemctl start barney-worker

# 3. Check Redis queue
redis-cli KEYS "*queue*"

# 4. Nuclear restart
sudo pkill -f worker.py && sleep 2 && sudo systemctl start barney-worker
```

---

## Test Backend Directly
```bash
# Health check
curl http://localhost:8000/

# Submit a task
curl -X POST http://localhost:8000/run_task \
  -H "x-api-key: your-secret" \
  -H "Content-Type: application/json" \
  -d '{"task": "hello", "user_id": "default"}'
```

---

## File Locations
| What | Where |
|---|---|
| Backend code | `~/Barney/barney_v2/` |
| Frontend code | `~/Barney/barneyUI/` |
| Worker log | `~/Barney/worker.log` |
| API log | `~/Barney/api.log` |
| Environment vars | `~/Barney/.env` |
| Venv | `~/Barney/venv/` |
| Systemd services | `/etc/systemd/system/barney-*.service` |