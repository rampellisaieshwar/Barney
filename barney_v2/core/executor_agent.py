from core.llm import call_llm
from core.tools import TOOLS
from redis_client import append_log

def dispatch_tool(tool: str, task: str, task_id: str = None) -> dict:
    """
    Central Dispatcher for Tool Execution.
    """
    if task_id:
        append_log(task_id, f"🔧 [Executor] Running tool: {tool}")

    result_context = ""
    tool_failed = False
    
    try:
        if tool == "search":
            result_context = TOOLS["search"](task)
        elif tool == "python":
            # For simplicity, pass the task directly to the python execution tool.
            # In a real scenario, LLM would generate the code first.
            # We'll just ask LLM to generate the code, then run it.
            code_prompt = f"Write python code to solve: {task}. Output ONLY raw python code."
            code_resp = call_llm(code_prompt, role="fast", task_id=task_id)
            code = code_resp.get("content", "").replace("```python", "").replace("```", "").strip()
            
            if task_id:
                append_log(task_id, f"🔧 [Executor] Executing Python:\n{code[:100]}...")
                
            result_context = TOOLS["python"]({"code": code})
        elif tool == "llm":
            result_context = "No external tool used. Use internal knowledge."
        else:
            result_context = f"Error: Tool '{tool}' is not recognized."
            tool_failed = True
            
        is_useless = any(marker in str(result_context).lower() for marker in ["no direct abstract", "error", "failed", "could not find"])
        if is_useless and tool != "llm":
             tool_failed = True
             result_context += "\n[SYSTEM ALERT]: The tool failed to produce useful information."

    except Exception as e:
        result_context = f"Error executing {tool}: {e}"
        tool_failed = True

    if task_id:
        log_snip = str(result_context)[:200].replace('\n', ' ')
        append_log(task_id, f"✅ [Executor] Tool result: {log_snip}...")

    # Final Synthesis
    if task_id:
        append_log(task_id, f"🧠 [Executor] Synthesizing final answer...")
        
    synth_prompt = (
        f"Task: {task}\n\n"
        f"Tool Used: {tool}\n"
        f"Tool Context:\n{result_context}\n\n"
        "Provide a clear, thorough, well-structured answer to the task based on the context. "
        "If the tools failed to find data, answer using your own general knowledge."
    )
    
    synth_resp = call_llm(synth_prompt, role="strong", task_id=task_id)
    final_answer = synth_resp.get("content", "Failed to generate answer.")
    confidence = synth_resp.get("confidence", 0.6)
    
    if tool_failed:
         confidence = min(confidence, 0.6)
         
    return {
        "status": "success" if not tool_failed else "fallback",
        "answer": final_answer,
        "confidence": confidence,
        "tool_context": result_context
    }
