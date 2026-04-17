# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Barney v2** is a governed autonomous agent framework for high-stakes research and tactical execution. It features trust-layered governance, adaptive strategy selection, and persistent memory.

The repository contains two main components:
- `barney_v2/` — Python backend (agent engine, API, memory)
- `barneyUI/` — React/TypeScript frontend

## Common Commands

### Backend (barney_v2)
```bash
# Install dependencies
pip install -r barney_v2/requirements.txt

# Run the production API server
python3 -m uvicorn api_server:app --port 8000

# Run the governance dashboard (Streamlit)
streamlit run app.py

# Run end-to-end validation
python3 validate_barney_e2e.py

# Run a single test
python3 -m pytest barney_v2/tests/test_loop.py -v

# Run the main demo
python3 barney_v2/main.py
```

### Frontend (barneyUI)
```bash
cd barneyUI && npm install && npm run dev
```

## Architecture

### Core Execution Flow
The main loop in `core/loop.py` orchestrates task execution:

1. **Planning** (`core/planner_agent.py`) — Generates strategic multi-step plans
2. **Strategy Selection** (`core/strategy.py`) — Chooses between `explore`, `search`, `compare`, `rank`, `validate` based on historical performance
3. **Execution** (`core/executor.py`) — Runs steps with tool calls and quality validation
4. **Memory** (`core/memory.py`) — Stores insights and computes strategy stats
5. **Grounding** (`core/grounding.py`) — Reality anchor for fact verification
6. **Risk Assessment** (`core/risk_assessor.py`) — Evaluates step risk, triggers human checkpoints

### Key Modules
| File | Purpose |
|------|---------|
| `core/loop.py` | Main execution loop, orchestrates all phases |
| `core/planner_agent.py` | Initial planning and replanning with HITL support |
| `core/executor.py` | Step-by-step execution with tool dispatch |
| `core/executor_agent.py` | Single-step executor with retry logic |
| `core/strategy.py` | Strategy selection with fatigue/recovery logic |
| `core/memory.py` | In-memory insight storage with strategy stats |
| `core/memory_manager.py` | Semantic retrieval from knowledge ledger |
| `core/qdrant_memory.py` | Vector-based semantic memory (Qdrant) |
| `core/tools.py` | Tool registry (search, python, file ops) |
| `core/llm.py` | LLM interface (Groq-based) |
| `core/grounding.py` | Reality anchoring and claim verification |
| `core/risk_assessor.py` | Risk scoring and decay logic |
| `core/scoring.py` | Depth scoring and semantic evaluation |
| `core/insight_engine.py` | Task type classification |
| `core/preprocessor.py` | Grounding requirement detection |
| `api_server.py` | FastAPI REST API with Redis state |
| `redis_client.py` | Redis state management |

### Execution Modes
- **Generative Preempt** — Direct LLM synthesis for stable tasks (code, creative)
- **Hybrid Fallback** — Partial grounding for mixed tasks
- **Deep Mode** — Full planner → executor loop for complex research
- **Simple Mode** — Fast-path for factual queries with real-time data

### Data Flow
- Tasks are enqueued via `api_server.py` → stored in Redis
- Worker processes tasks through the loop
- State checkpoints saved to Redis for resume
- Final results stored with quality metrics

## Environment Variables
Environment config is in `barney_v2/.env`:
- `GROQ_API_KEY` — Groq LLM backend
- `REDIS_URL` — Redis connection
- `QDRANT_URL` — Vector memory (optional)
- `BARNEY_API_KEY` — API authentication