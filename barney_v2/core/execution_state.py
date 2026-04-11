import uuid
import json

class ExecutionState:
    """
    Persistence layer for Barney's governance loop.
    Ensures that 'Pauses' for human input don't lose context.
    """
    def __init__(self, task: str, task_id: str = None):
        self.task_id = task_id if task_id else str(uuid.uuid4())[:8]
        self.task = task
        self.plan = []
        self.current_step_index = 0
        self.replan_counter = 0
        self.correction_count = 0
        self.status = "INIT"
        self.history = []
        self.history_text = ""
        self.constraints = {}
        self.logs = []
        self.result = None
        self.risk_scores = {}
        self.cumulative_risk = 0.0
        self.wait_start_time = 0.0
        self.completed_step_ids = [] # List of hashes for idempotency
        self.strategy_type = "explore"
        self.strategy_info = {}
        self.grounding_data = {}
        self.confidence = 0.0
        self.meta = {}
        self.is_generative_override = False
        self.is_hybrid_fallback = False
        self.wait_start_time = 0.0

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        state = cls(data["task"], data.get("task_id"))
        state.__dict__.update(data)
        return state

    def save(self):
        """Atomic persistence for state synchronization."""
        import os
        from core.tools import _secure_path
        task_dir = os.path.join("barney_data", "tasks")
        os.makedirs(task_dir, exist_ok=True)
        path = os.path.join(task_dir, f"{self.task_id}.json")
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def add_log(self, step_idx, decision, risk_score, reason, log_type="AUTO_EXECUTION", risk_before=0.0, risk_after=0.0, step_id=None):
        """Audit trail for diagnostic-grade observation."""
        self.logs.append({
            "step_index": step_idx,
            "decision": decision, 
            "risk_score": risk_score,
            "risk_before": risk_before,
            "risk_after": risk_after,
            "reason": reason,
            "log_type": log_type, # RISK_DECISION, HUMAN_OVERRIDE, AUTO_EXECUTION
            "step_id": step_id,
            "timestamp": None
        })
