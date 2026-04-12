# System Design & Architecture Report: Barney v2

## 1. Executive Summary
Barney v2 is an advanced autonomous agent system designed for complex task execution. It leverages a decoupled architecture consisting of a React-based frontend and a Python-based backend powered by FastAPI and Redis. The system implements a sophisticated "Plan-Execute-Verify" loop, utilizing multi-role LLM orchestration to balance execution speed with reasoning quality.

---

## 2. Project Structure
The codebase is split into two primary domains:

### 📁 `barneyUI/` (Frontend)
A modern, single-page application (SPA) providing an OS-like interface for task management, real-time log monitoring, and system configuration.

### 📁 `barney_v2/` (Backend)
The core intelligence engine. It handles API requests, task queuing, agentic reasoning, and tool execution.
- `core/`: The "brain" containing planner, executor, memory, and grounding logic.
- `barney_data/`: Local state and data persistence.
- `tests/` & `stress_tests/`: Comprehensive validation suites.

---

## 3. Architecture Deep Dive

### 🎨 Frontend Architecture
- **Stack**: React 19, TypeScript, Vite, Tailwind CSS 4.0.
- **UI/UX**: Uses `motion` for fluid animations and `lucide-react` for iconography.
- **State Management**: Managed via React hooks (`useState`, `useEffect`), focusing on a `currentView` state to toggle between the Console and Settings.
- **Communication**: A dedicated `api.ts` layer handles RESTful communication with the backend, implementing polling for task status and Server-Sent Events (SSE)/WebSockets for real-time log streaming.

### ⚙️ Backend Architecture
- **API Layer**: FastAPI running on Uvicorn, providing high-performance asynchronous endpoints.
- **Task Orchestration**: 
  - **Redis**: Serves as the central message broker and state store. It manages the task queue, caches intermediate results (idempotency), and tracks agent "heartbeats" to prevent zombie processes.
  - **Worker Pattern**: `worker.py` implements a resource-aware consumer that dequeues tasks and manages their lifecycle.
- **Agent Intelligence (`core/`)**:
  - **The Governed Loop (`loop.py`)**: A state machine that manages the transition between Planning $\rightarrow$ Executing $\rightarrow$ Human Intervention $\rightarrow$ Completion.
  - **Multi-Role Execution**: Uses a "Strong" model for complex/risky reasoning and a "Fast" model for routine steps to optimize cost and latency.
  - **Grounding & Verification**: `RealityAnchor` ensures that the agent's claims are backed by retrieved data, and `verify_step_outcome` validates that each plan step actually succeeded before moving forward.

---

## 4. Data Flow & Request Lifecycle

1. **Submission**: User submits a goal via the `TaskConsole` $\rightarrow$ POST `/run_task`.
2. **Ingestion**: FastAPI validates the request $\rightarrow$ Task is pushed to the Redis queue.
3. **Activation**: `worker.py` picks up the task $\rightarrow$ initializes the `loop.py` state machine.
4. **Planning**: `planner_agent` decomposes the goal into a structured, multi-step execution plan.
5. **Execution Cycle**:
   - `executor_agent` picks a step $\rightarrow$ selects the appropriate LLM role.
   - Tool execution $\rightarrow$ Result is cached in Redis.
   - `verify_step_outcome` checks the result against the goal.
6. **Closing**: `SemanticEvaluator` performs a final quality check on the answer.
7. **Delivery**: Frontend polls `/status/{task_id}` $\rightarrow$ UI renders the final answer and execution logs.

---

## 5. Infrastructure & Deployment
- **Frontend**: Targeted for Vercel deployment (`vercel.json`).
- **Backend**: Containerized via `Dockerfile` for consistent environment reproduction.
- **Environment**: Managed via `.env` for API keys and infrastructure endpoints (Redis).

## 6. Key Dependencies
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **LLM Orchestration** | Groq / Google GenAI | Core reasoning and generation |
| **State Store** | Redis | Queueing, caching, and heartbeat monitoring |
| **API Framework** | FastAPI | High-performance async REST API |
| **UI Framework** | React 19 / Vite | Responsive, type-safe frontend |
| **Validation** | Pydantic | Data modeling and request validation |
