# 🛡️ Barney v2: The Governed Execution Engine

**Barney v2** is a production-grade autonomous agent framework designed for high-stakes research, tactical execution, and human-in-the-loop (HITL) governance. Unlike traditional agents that fail silently or hallucinate actions, Barney is built with **Terminal Honesty**, **Adaptive Intelligence**, and **Persistent Governance**.

---

## 🌟 Vision
Barney transforms from a "clever demo" into a reliable partner by ensuring that every movement—from planning to file modifications—is justified, verified, and governed.

---

## 🚀 core Features

### 1. 🛡️ Trust-Layered Governance (Phase 11.5)
Every high-risk action requires:
- **Pre-Execution Justification**: Why is this step necessary?
- **Post-Execution Verification**: Did the step achieve its intent?
- **Human Intercepts**: Automated halting for High-Risk contexts.

### 2. 🧠 Adaptive Research Mastery (Phase 12)
- **Strategy Selection**: Dynamically weights strategies based on past success.
- **Memory Reuse**: Leverages prior insights to minimize redundant tool calls and API costs.
- **Deep Analytical Chains**: Multi-iteration reasoning for complex research.

### 3. 🚨 resilient Intelligence (Phase 12.5)
- **BRAIN_DEAD Awareness**: System automatically detects brain-disconnection (LLM failure) and transitions to a terminal "honesty" state instead of failing silently.
- **Retry Layer**: Robust API resilience with exponential backoff.

### 4. 📂 Atomic Persistence (Phase 13)
- **Versioned Memory**: Versioned `knowledge_ledger.json` with auto-pruning (N=5).
- **Task Lifecycles**: Every task state is persisted to `barney_data/tasks/`, allowing for recovery and audit.

### 5. 🌐 Production API (Phase 14)
- **FastAPI Core**: A RESTful gateway to the Barney engine.
- **Async Simulation**: `BackgroundTasks` enable non-blocking task submission and polling.
- **Redis State Tracking**: Atomic status management available via `/status/{task_id}`.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Redis (for API service)
- Groq API Key (for LLM backend)

### 1. Environment Configuration
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_key_here
REDIS_HOST=localhost
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🎮 Running Barney

### 📡 The Production API
```bash
python3 -m uvicorn api_server:app --port 8000
```

### 🛡️ The Governance Dashboard (Streamlit)
```bash
streamlit run app.py
```

### 🧪 End-To-End Validation
```bash
python3 validate_barney_e2e.py
```

---

## 📦 Containerization
```bash
docker build -t barney-api .
docker run -p 8000:8000 -e GROQ_API_KEY=$GROQ_API_KEY barney-api
```

---

## 📜 Repository Structure
- `core/`: The engine (Planner, Executor, Memory, Trust, Risk).
- `api_server.py`: FastAPI implementation.
- `app.py`: Streamlit UI.
- `barney_data/`: Persistent task logs and knowledge ledger.

---
**Barney v2: Autonomous. Governed. Honest.**
