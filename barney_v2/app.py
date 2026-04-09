import streamlit as st
import sys
import os
import json
import time

# Add barney_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loop import run_task
from core.execution_state import ExecutionState
from core.human_checkpoint import HumanCheckpoint
from core.risk_assessor import assess_risk

st.set_page_config(page_title="Barney AI Agent (Governance Mode)", page_icon="🛡️", layout="wide")

st.title("🛡️ Barney AI Agent v2.5")
st.subheader("Governed Multi-Agent Pipeline (Phase 8: HITL)")
st.markdown("---")

# Session State Initialization
if "execution_state" not in st.session_state:
    st.session_state.execution_state = None
if "last_task" not in st.session_state:
    st.session_state.last_task = ""

# Sidebar Control
with st.sidebar:
    st.title("System Controls")
    if st.button("🗑️ Reset session"):
        st.session_state.execution_state = None
        st.session_state.last_task = ""
        st.rerun()
    
    st.info("Phase 8 Governance: Every high-risk step is intercepted for your approval.")
    
    st.markdown("---")
    with st.expander("📊 Workspace Audit", expanded=False):
        manifest_path = "barney_data/manifest.json"
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)[-10:] # Show last 10
                for entry in reversed(manifest):
                    color = "blue" if entry['action'] == "WRITE" else "green" if entry['action'] == "READ" else "grey"
                    st.markdown(f"**{entry['file']}** ({entry['action']})\n- *{entry['intent']}*")
            except: st.write("Manifest corrupted...")
        else:
            st.write("No manifest found.")

# User Input
task = st.text_input("Enter your task:", placeholder="e.g., Calculate BTC trend (High Risk) or 2+2 (Low Risk)")

if st.button("🚀 Run Workflow") and task:
    st.session_state.last_task = task
    # Start fresh
    with st.spinner("Initializing Planning & Governance..."):
        res = run_task(task)
        if res.get("state"):
            st.session_state.execution_state = res["state"]
        st.rerun()

# 🛡️ MAIN GOVERNANCE LOOP UI
if st.session_state.execution_state:
    state_dict = st.session_state.execution_state
    state = ExecutionState.from_dict(state_dict)
    
    # 🧠 Planning View
    st.write(f"### 🎯 Task: {state.task}")
    
    # Risk Indicators
    risk_val = getattr(state, 'cumulative_risk', 0.0)
    risk_color = "red" if risk_val > 0.8 else "orange" if risk_val > 0.4 else "green"
    st.write(f"**Execution Status:** `{state.status}` | **Cumulative Risk:** :{risk_color}[{risk_val:.2f} / 0.80]")
    
    plan_col, risk_col = st.columns([2, 1])
    
    with plan_col:
        st.markdown("#### 📋 Planned Steps")
        for i, s in enumerate(state.plan):
            color = "green" if i < state.current_step_index else "blue" if i == state.current_step_index else "grey"
            st.markdown(f"<span style='color:{color}'>{i+1}. {s}</span>", unsafe_allow_html=True)

    with risk_col:
        st.markdown("#### 🛡️ Risk Assessment")
        for i, r in state.risk_scores.items():
            level = r['risk_level']
            color = "red" if level == "HIGH" else "orange" if level == "MEDIUM" else "green"
            st.markdown(f"**Step {int(i)+1}:** :{color}[{level}] ({r['risk_score']})")

    st.markdown("---")

    # 👤 HUMAN INTERVENTION PANEL
    if state.status == "WAITING_FOR_HUMAN":
        wait_start = getattr(state, "wait_start_time", 0)
        current_wait = time.time() - wait_start if wait_start > 0 else 0
        
        st.warning(f"🚨 **HIGH RISK DETECTED: Awaiting Governance Decision ({int(current_wait)}s)**")
        
        idx = state.current_step_index
        step_text = state.plan[idx]
        risk_info = state.risk_scores.get(str(idx)) or state.risk_scores.get(idx)
        
        st.write(f"**Intercepted Step:** `{step_text}`")
        st.write(f"**Risk Reason:** {risk_info.get('reason', 'High cumulative exposure')}")
        
        # 🧠 Trust Layer: Justification Panel (Phase 11.5)
        # Find the justification from the most recent executed step if available, 
        # or wait for the executor to provide it.
        with st.expander("🧠 View Tactical Justification", expanded=True):
            st.info("The agent is required to rationalize its strategy before this high-risk action.")
            # For a waiting step, we show the intention from the planner
            st.markdown(f"**Intent:** {step_text}")
            st.markdown(f"**Expected Outcome:** Successful execution of the tactical directive.")
            st.markdown(f"**Risk Reason:** Physical side-effect or cumulative exposure threshold breach.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ APPROVE STEP", type="primary", use_container_width=True):
                # 🛡️ Race Condition Guard: flag as deliberate approval
                state_dict = state.to_dict()
                state_dict["approved_step"] = True 
                res = run_task(state.task, state_dict=state_dict)
                st.session_state.execution_state = res["state"]
                st.rerun()

        with col2:
            mod_text = st.text_input("Modify Step Content:", value=step_text)
            if st.button("📝 MODIFY & RUN", use_container_width=True):
                from core.risk_assessor import assess_risk
                new_risk = assess_risk(mod_text, state.history, prev_cumulative=state.cumulative_risk)
                state.plan[idx] = mod_text
                state.risk_scores[idx] = new_risk
                state.status = "HUMAN_APPROVED"
                st.session_state.execution_state = run_task(state.task, state_dict=state.to_dict())["state"]
                st.rerun()

        with col3:
            rejection_reason = st.text_input("Reason for rejection:", placeholder="e.g., Too dangerous")
            if st.button("❌ REJECT & REPLAN", type="secondary", use_container_width=True):
                from core import planner_agent
                feedback = {"type": "HUMAN_FEEDBACK", "reason": rejection_reason, "priority": "HARD"}
                new_plan = planner_agent.replan(state.task, feedback)
                state.plan = new_plan.get("steps", [])
                state.current_step_index = 0
                state.replan_counter = getattr(state, 'replan_counter', 0) + 1
                state.status = "PLANNING"
                st.session_state.execution_state = state.to_dict()
                st.rerun()

    # ⚙️ CONTINUING EXECUTION
    elif state.status == "EXECUTING":
        with st.spinner("Executing current step..."):
            res = run_task(state.task, state_dict=state.to_dict())
            st.session_state.execution_state = res["state"]
            st.rerun()

    # 🏁 FINAL STATES
    elif state.status == "COMPLETED":
        st.success("🏁 Task Completed Successfully")
        st.markdown(f"#### Final Answer:\n{state.result}")
        
        with st.expander("🛠️ View Detailed Trust Audit", expanded=False):
            for i, h in enumerate(state.history):
                st.markdown(f"---")
                st.markdown(f"**Step {i+1}: {h.get('executed_step', 'Unknown')}**")
                
                # Trust Info
                v = h.get("verification", {})
                j = h.get("justification", {})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"🧠 **Intent:** {j.get('intent', 'N/A')}")
                    st.write(f"✅ **Verdict:** {v.get('verdict', 'N/A')}")
                with col2:
                    st.write(f"🎯 **Confidence:** {v.get('confidence', 0.0)*100:.0f}%")
                    st.write(f"📂 **Evidence:** {v.get('evidence', 'N/A')}")
        
        with st.expander("📝 View Raw Execution Logs"):
            st.table(state.logs)

    elif state.status == "REJECTED_TIMEOUT":
        st.error("🚨 GOVERNANCE FAILURE: High-Risk Safety Timeout")
        st.write("The system auto-rejected the task because no human response was received within the safety window.")
        if st.button("🔄 Restart Task"):
            st.session_state.execution_state = None
            st.rerun()

    elif state.status == "FAILED":
        st.error("❌ Task Execution Failed")
        st.write(state.history[-1].get("reason") if state.history else "Unknown error")
