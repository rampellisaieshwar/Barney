from typing import Literal

DecisionAction = Literal["APPROVE", "MODIFY", "REJECT"]

class HumanCheckpoint:
    """
    State-Aware Handler for Human Decision Intervention.
    Captures intent for both CLI and UI.
    """
    def __init__(self, step_idx: int, step_desc: str, risk_info: dict):
        self.step_idx = step_idx
        self.step_desc = step_desc
        self.risk_info = risk_info
        self.decision = None # Will store the choice (APPROVE, MODIFY, REJECT)
        self.updated_step = None 
        self.feedback = None

    def approve(self):
        self.decision = "APPROVE"
        return {"action": "APPROVE"}

    def modify(self, new_step: str):
        self.decision = "MODIFIED"
        self.updated_step = new_step
        return {"action": "MODIFY", "updated_step": new_step}

    def reject(self, reason: str, priority: str = "HARD"):
        self.decision = "REJECTED"
        self.feedback = {
            "type": "HUMAN_FEEDBACK",
            "failed_step": self.step_desc,
            "reason": reason,
            "priority": priority, # HARD = must be a planning constraint
            "instruction": f"Avoid similar mistakes: {reason}"
        }
        return {"action": "REJECT", "feedback": self.feedback}

    def to_cli(self):
        """CLI Pause for Terminal Verification."""
        print(f"\n🛑 HUMAN CHECKPOINT [Step {self.step_idx+1}]")
        print(f"   Step: {self.step_desc}")
        print(f"   Risk: {self.risk_info['risk_level']} ({self.risk_info['risk_score']})")
        print(f"   Reason: {self.risk_info['reason']}")
        
        choice = input("\n[A]pprove, [M]odify, [R]eject? ").strip().lower()
        if choice == 'a': return self.approve()
        if choice == 'm': 
            new_text = input("Enter corrected step: ")
            return self.modify(new_text)
        if choice == 'r':
            reason = input("Reason for rejection: ")
            return self.reject(reason)
        return self.approve() # Default
