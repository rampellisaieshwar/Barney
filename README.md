# 🤖 Barney v2 — Autonomous AI Agent Platform

> *"Have you met Barney?"*

Barney is a self-building autonomous AI agent platform. It doesn't just answer questions — it decides **how** to answer them, writes its own tools, calls real APIs, and adapts its strategy based on what it discovers mid-task.

---

## ✨ What Makes Barney Different

Most AI apps wrap ChatGPT and return a response. Barney has its own **routing brain**:

- **Generative tasks** (code, essays, math) → answered directly in one LLM call
- **Real-time tasks** (weather, prices, news) → grounds itself with live data first
- **Complex tasks** (comparisons, research) → plans multi-step strategy, executes, critiques, replans if needed
- **API tasks** (anything needing external services) → writes Python code, requests credentials from user, runs the code, returns real data

---

## 🧠 Architecture

```
User Request
    ↓
┌─────────────────────────────────┐
│         Routing Brain           │
│  Generative? → Direct LLM      │
│  Real-time?  → Ground + Synth  │
│  Agent Mode? → Tool Builder    │
│  Complex?    → Planning Loop   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│         Execution Layer         │
│  Planner Agent                  │
│  Executor Agent                 │
│  Critic Agent (4-layer)         │
│  ReAct Loop                     │
│  Self-Correction                │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│         Agent Creation Mode     │
│  Detects API need               │
│  Requests credentials           │
│  Writes + runs Python code      │
│  Encrypted Credential Vault     │
└─────────────────────────────────┘
    ↓
Final Answer
```

---

## 🚀 Features

### Core Intelligence
- **Generative Preempt** — coding/creative tasks bypass the research pipeline entirely
- **ReAct Loop** — Thought → Action → Observation reasoning cycle
- **4-layer Critic Agent** — evaluates answer quality before returning
- **Self-Correction** — replans up to 2x if grounding score is low
- **Semantic Memory** — learns from past tasks, weights recent insights higher

### Agent Creation Mode
- Detects when a task needs an external API (weather, stocks, news, crypto)
- Asks user for API key via natural language
- Stores key encrypted in Redis vault
- Writes Python code dynamically via LLM
- Executes code in subprocess on the VM
- Reuses stored keys automatically next time

### Infrastructure
- **FastAPI** backend with SSE streaming and WebSocket support
- **Redis** for task queuing, state, logs, credential vault
- **Groq API** (llama-3.3-70b-versatile) as primary LLM
- **Systemd** services for auto-restart on crash
- **Vercel** frontend with proxy to Azure VM backend
- Priority queue with fairness and cost-aware scheduling
- Idempotent step execution with distributed locking

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (llama-3.3-70b-versatile / llama-3.1-8b-instant) |
| Backend | FastAPI + Python 3.12 |
| Queue | Redis Streams |
| Memory | Redis + Qdrant (vector search) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Frontend | React + TypeScript + Vite + Tailwind |
| Hosting | Azure VM (backend) + Vercel (frontend) |
| Credential Vault | Redis + Fernet AES encryption |

---

## 📁 Project Structure

```
barney_v2/
├── core/
│   ├── loop.py                  # Main execution router
│   ├── planner_agent.py         # Strategic planning
│   ├── executor_agent.py        # Step execution
│   ├── critic.py                # Answer quality evaluation
│   ├── llm.py                   # LLM interface (Groq)
│   ├── tools.py                 # Web search, file ops, Python runner
│   ├── memory.py                # Task memory + insights
│   ├── preprocessor.py          # Intent detection + grounding
│   ├── grounding.py             # Reality anchoring
│   ├── scoring.py               # Semantic quality scoring
│   └── agent_mode/
│       ├── agent_creation_handler.py  # Agent mode orchestrator
│       ├── tool_builder_v2.py         # Dynamic code generation
│       └── credential_vault.py        # Encrypted API key storage
├── worker.py                    # Task queue worker
├── api_server.py                # FastAPI routes
├── redis_client.py              # Redis interface
└── requirements.txt
barneyUI/
├── src/
│   ├── components/
│   │   ├── TaskConsole.tsx      # Main chat interface
│   │   ├── Settings.tsx         # Agent mode toggle + settings
│   │   └── PlanVisualizer.tsx   # Step trace visualizer
│   └── services/
│       └── api.ts               # Backend communication
└── vercel.json                  # Proxy config
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.12+
- Redis
- Groq API key (free at console.groq.com)
- Node.js 18+ (for frontend)

### Backend

```bash
# Clone repo
git clone https://github.com/rampellisaieshwar/barney
cd barney/barney_v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your keys to .env

# Generate vault key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add output as VAULT_KEY in .env

# Start API
uvicorn api_server:app --port 8000 --host 0.0.0.0

# Start worker (separate terminal)
python worker.py
```

### Frontend

```bash
cd barneyUI
npm install

# Set environment variables
echo "VITE_API_BASE=/api" > .env.local
echo "VITE_API_KEY=your-secret" >> .env.local

npm run dev
```

### Environment Variables

```env
GROQ_API_KEY=           # Required — get from console.groq.com
VAULT_KEY=              # Required — generate with Fernet
REDIS_URL=              # Default: redis://localhost:6379/0
BARNEY_API_KEY=         # API key for frontend authentication
OPENAI_API_KEY=         # Optional fallback
SECRET_KEY=             # Session secret
```

---

## 🧪 Testing Agent Mode

```bash
# Turn on agent mode
curl -X POST http://localhost:8000/agent_mode/toggle \
  -H "x-api-key: your-secret" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "default", "enabled": true}'

# Ask a weather question → Barney requests your OpenWeather key
# Re-ask with key:
# KEY=OPENWEATHER_API_KEY=your_key_here What's the weather in Hyderabad?

# Ask again → uses stored key automatically
```

---

## 🗺 Roadmap

- [ ] Per-user authentication and credential isolation
- [ ] Tool registry with caching (skip code generation for known APIs)
- [ ] WebSocket live streaming (currently polling)
- [ ] More API detections (flights, maps, email)
- [ ] Agent-to-agent delegation
- [ ] Usage dashboard

---

## 👤 Author

**Rampelli Sai Eshwar**  
Applied AI Engineer  
[LinkedIn](https://linkedin.com/in/saieshwarrampelli) · [GitHub](https://github.com/rampellisaieshwar) · [Portfolio](https://saieshwarrampelli.vercel.app)

---

## 📄 License

MIT License — use freely, attribution appreciated.