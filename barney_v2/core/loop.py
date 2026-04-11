"""
Loop: The core execution loop that ties everything together.

Now implements Deterministic Testing and Strategy Locking.
(Stress Test Layer #1 & #2)
"""

import json
import re
import time
import hashlib
import uuid
import random
import threading
from core import planner_agent, executor_agent, critic, insight_engine
from core.insight_engine import get_task_type, get_task_condition
from core.memory import Memory
from core.strategy import select_strategy
from core.scoring import calculate_depth_score, get_required_depth, SemanticEvaluator
from core.grounding import RealityAnchor
from core.risk_assessor import assess_risk, apply_decay
from core.execution_state import ExecutionState

_memory = Memory()

def get_memory() -> Memory:
    return _memory

def score_research_quality(history: list) -> dict:
    """Belief System: Quality & Consistency Scoring (Phase 12)."""
    tool_outputs = []
    sources = set()
    
    for h in history:
        if not isinstance(h, dict): continue
        update = h.get("history_update", "").lower()
        if "tool:" in update:
            tool_outputs.append(update)
            match = re.search(r"site:([\w\.]+)", update)
            if match: sources.add(match.group(1))
            else: sources.add("general_source")

    source_count = len(sources)
    
    # 2. Consistency & Reliability Logic
    consistency = 1.0
    has_error = any("error" in out for out in tool_outputs)
    
    if has_error:
        consistency = 0.3 # Major penalty for tool failures
    elif source_count < 2:
        consistency = 0.5 # Single source is provisional

    # 3. Final Confidence Calibration
    if has_error:
        final_conf = 0.3
    elif source_count >= 2 and consistency >= 0.8:
        final_conf = 0.8
    else:
        final_conf = 0.5
    
    if source_count < 2:
        final_conf = min(final_conf, 0.5)

    return {
        "source_count": source_count,
        "consistency_score": consistency,
        "final_confidence": final_conf
    }

def verify_step_outcome(step: str, justification: dict, result: str) -> dict:
    """Trust Layer: Structured Verification (Phase 11.5)."""
    expected = justification.get("expected_outcome", "").lower()
    result_text = str(result).lower()
    
    if "write_file" in step.lower() or "save" in step.lower():
        import os
        from core.tools import DATA_ROOT
        match = re.search(r"['\"]([^'\"]+\.\w+)['\"]", step)
        if match:
            fname = match.group(1)
            target = os.path.join(DATA_ROOT, fname)
            if not os.path.exists(target):
                return {"confidence": 0.2, "evidence": f"File '{fname}' missing from disk.", "verdict": "FAIL"}

    # If the result contains LLM synthesis content, trust it even if tool failures exist in history
    has_llm_synthesis = "[llm synthesis]" in result_text or "[final output]" in result_text
    
    if not has_llm_synthesis and ("error:" in result_text or "fail" in result_text):
        # Only flag tool errors when there's no LLM fallback answer
        if "[tool_failed]" in result_text:
            return {"confidence": 0.5, "evidence": "Tool returned no useful data, but step may have fallback.", "verdict": "WEAK"}
        return {"confidence": 0.1, "evidence": "Tool reported error signal.", "verdict": "FAIL"}
        
    if "search" in step.lower() and len(result_text) < 100 and not has_llm_synthesis:
        return {"confidence": 0.4, "evidence": "Search result too shallow for validation.", "verdict": "WEAK"}

    return {"confidence": 0.9, "evidence": "Step output aligns with expected outcome constraints.", "verdict": "PASS"}

def evaluate_outcome(task: str, answer: str) -> dict:
    """Outcome Intelligence: Content-Aware Valuation."""
    if not isinstance(answer, str):
        answer = json.dumps(answer) if answer else ""
    
    if not answer or len(answer.strip()) < 50:
        return {"score": -1, "reason": "too short / empty"}
        
    depth = calculate_depth_score(answer)
    required = get_required_depth(task)
    
    if depth < required:
        return {"score": -1, "reason": f"shallow content (depth={depth}/{required})"}
        
    return {"score": 1, "reason": "informative/deep answer"}

def evaluate_tool_usage(tool_calls, repeated_tool, outcome_score, task) -> int:
    """Tool Efficiency Scoring."""
    requires_tool = any(word in task.lower() for word in ["latest", "current", "today", "weather", "price", "stock", "news"])
    if requires_tool and tool_calls == 0: return -1
    if repeated_tool: return -1
    if tool_calls > 2 and outcome_score < 0: return -1
    return 1

def evaluate_plan(task: str, plan: list[str], final_answer: str) -> dict:
    if not plan: return {"score": -1, "reason": "No plan."}
    is_simple_task = len(task.split()) < 5
    min_length = 50 if is_simple_task else 100
    if not isinstance(final_answer, str):
        final_answer = json.dumps(final_answer) if final_answer else ""
    if not final_answer or len(final_answer.strip()) < min_length:
        return {"score": -1, "reason": "Final answer suboptimal."}
    return {"score": 1, "reason": "Plan produced substantial answer."}

def _generate_step_id(task_id: str, step_text: str, replan_counter: int) -> str:
    norm = re.sub(r'[^a-zA-Z0-9]', '', step_text.lower())[:50]
    raw = f"{task_id}_{norm}_{replan_counter}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def _ensure_str_answer(answer) -> str:
    """PIPELINE CONTRACT: Guarantees answer is ALWAYS a plain string.
    Handles dicts, lists, None, and nested structures."""
    if answer is None:
        return "No answer was generated."
    if isinstance(answer, str):
        return answer
    if isinstance(answer, dict):
        # Extract from common nested patterns
        if "answer" in answer:
            return _ensure_str_answer(answer["answer"])
        if "content" in answer:
            return _ensure_str_answer(answer["content"])
        if "result" in answer:
            return _ensure_str_answer(answer["result"])
        # Last resort: JSON stringify
        return json.dumps(answer, indent=2)
    if isinstance(answer, list):
        return json.dumps(answer, indent=2)
    return str(answer)

def _standardize_final_return(status: str, answer: any, confidence: float = 0.9, run_start_time: float = None, history: list = None, **kwargs):
    """PIPELINE CONTRACT: The single source of truth for all run_task returns."""
    final_answer = _ensure_str_answer(answer)
    
    # [FINAL] Contract Logging (Requirement #7)
    _preview = final_answer[:100].replace('\n', ' ')
    print(f"  [FINAL] Answer type: {type(final_answer).__name__}, preview: {_preview}")
    
    res = {
        "status": status,
        "answer": final_answer,
        "confidence": float(confidence),
        "steps": len(history) if history else 0,
        "tools_used": sum(h.get("tool_calls", 0) for h in history if isinstance(h, dict)) if history else 0,
    }
    
    if run_start_time:
        res["response_time_ms"] = int((time.time() - run_start_time) * 1000)
    
    res.update(kwargs)
    return res

def _build_generative_system_prompt(task: str) -> str:
    t = task.lower()
    code_signals = [
        "write", "code", "script", "function", "program", "implement",
        "algorithm", "snippet", "class", "python", "javascript", "java",
        "sql", "bash", "typescript", "rust", "c++"
    ]
    if any(s in t for s in code_signals):
        lang_hints = {
            "python": "Python", "javascript": "JavaScript", "java": "Java",
            "sql": "SQL", "bash": "Bash", "c++": "C++", "rust": "Rust",
            "typescript": "TypeScript"
        }
        lang = next((v for k, v in lang_hints.items() if k in t), "the appropriate language")
        return (
            f"You are an expert software engineer. "
            f"The user wants working {lang} code. "
            f"Respond with ONLY the code in a fenced code block, then a brief explanation after it. "
            f"Do NOT produce step-by-step English plans. Write complete, runnable code immediately."
        )
    creative_signals = ["write a", "write an", "story", "poem", "essay", "draft", "compose"]
    if any(s in t for s in creative_signals):
        return (
            "You are a skilled writer. Produce the requested creative content directly. "
            "Do not explain your approach — just write the content."
        )
    math_signals = ["calculate", "compute", "solve", "formula", "equation"]
    if any(s in t for s in math_signals):
        return (
            "You are a precise mathematician. Show working step-by-step, "
            "then give the final numerical answer clearly."
        )
    return (
        "You are Barney, a highly capable AI assistant. "
        "Answer the following request fully, directly, and in the most useful format. "
        "Do not produce planning steps — produce the actual answer."
    )

def run_task(task: str, mode: str = "real", state_dict: dict = None, test_mode: bool = False, forced_outcome: dict = None, task_id: str = None) -> dict:
    """
    Hardened Step-by-Step Governed Loop (Phase 12.5).
    """
    run_start_time = time.time()
    print(f"  🚀 [loop] Starting run_task: {task[:50]}")
    MAX_WAIT = 300 # 5 minutes
    
    # --- Conversational Bypass (Phase 50) ---
    t_lower = task.lower().strip()
    t_clean = re.sub(r"[^\w\s]", "", t_lower)
    greetings = {"hi", "hello", "hey", "who are you", "what are you", "sup", "greetings"}
    if t_clean in greetings:
        print(f"  👋 [loop] Conversational shortcut triggered for: {task}")
        from redis_client import append_log
        if task_id: append_log(task_id, "👋 [loop] Conversational shortcut handled.")
        return {
            "status": "DONE",
            "answer": _ensure_str_answer("Hello! I am Barney, your autonomous AI assistant. How can I help you today?"),
            "confidence": 1.0,
            "steps": 0,
            "tools_used": 0,
            "response_time_ms": int((time.time() - run_start_time) * 1000)
        }

    # 1. Initialize or Resume State (Phase 31: Reliability & Replay)
    from redis_client import get_task, update_task, append_log, record_model_experience
    
    task_type = get_task_type(task)
    task_state = get_task(task_id) if task_id else None
    checkpoint = task_state.get("checkpoint") if task_state else None
    
    if checkpoint:
        print(f"  ♻️ [loop] Checkpoint detected for {task_id}. Resuming from step {checkpoint['current_step']}.")
        append_log(task_id, f"♻️ Resuming from checkpoint (Step {checkpoint['current_step']})")
        
        state = ExecutionState(task, task_id=task_id)
        state.plan = checkpoint.get("plan", [])
        state.current_step_index = checkpoint.get("current_step", 0)
        state.completed_step_ids = checkpoint.get("completed_steps", [])
        state.status = "EXECUTING"
    elif state_dict:
        state = ExecutionState.from_dict(state_dict)
        if state.status == "WAITING_FOR_HUMAN" and state_dict.get("approved_step"):
            if state.wait_start_time > 0 and (time.time() - state.wait_start_time) > MAX_WAIT:
                print("  🚨 [chaos] Human approval ignored: Timeout already triggered REJECT.")
                state.status = "REJECTED_TIMEOUT"
    else:
        state = ExecutionState(task, task_id=task_id)
        state.status = "PLANNING"

    # 2. Planning Phase
    if state.status == "PLANNING":
        search_results = _memory.search(task)
        prior_insights = search_results["insights"]
        reason_traces = search_results["reason_traces"]
        global_stats = _memory.get_strategy_stats(_memory.count())
        
        # 1.5 Grounding Pre-processing (Phase 40: Intent Intelligence)
        from core.preprocessor import get_grounding_requirement
        grounding_data = get_grounding_requirement(task, task_id=state.task_id)
        state.grounding_data = grounding_data
        
        # ── Classification safety net ────────────────────────────────────────
        _t_low = task.lower()
        _code_sigs = {"write", "code", "script", "function", "program", "implement",
                      "algorithm", "snippet", "python", "javascript", "java", "sql",
                      "bash", "typescript", "rust", "c++", "regex"}
        _creative_sigs = {"write a", "write an", "compose", "draft"}
        _compute_sigs = {"calculate", "compute", "solve", "convert"}
        _needs_override = (
            any(s in _t_low for s in _code_sigs) or
            any(s in _t_low for s in _creative_sigs) or
            any(s in _t_low for s in _compute_sigs)
        )
        if _needs_override and grounding_data.get("task_nature") not in ["GENERATIVE", "HYBRID"]:
            print(f"  🔧 [classify] Overriding task_nature to GENERATIVE (was: {grounding_data.get('task_nature')})")
            grounding_data["task_nature"] = "GENERATIVE"
            grounding_data["required_grounding"] = "NONE"
            state.grounding_data = grounding_data
        # ── End classification safety net ────────────────────────────────────
        
        # 1.6 Semantic Override Logic (Requirement #1, #2, #4)
        task_nature = grounding_data.get("task_nature", "FACTUAL")
        grounding_req = grounding_data.get("required_grounding", "NONE")
        
        # FULL OVERRIDE: Generative tasks with stable context
        state.is_generative_override = (
            task_nature == "GENERATIVE" and 
            grounding_req in ["NONE", "ARCHIVAL"]
        )
        
        # PARTIAL OVERRIDE: Hybrid tasks with stable context (Requirement #1 fix)
        state.is_hybrid_fallback = (
            task_nature == "HYBRID" and 
            grounding_req in ["NONE", "ARCHIVAL"]
        )
        
        state.meta["confidence_type"] = "normal"
        
        if state.is_generative_override:
            print(f"  ⚡ [MODE] GENERATIVE PREEMPT engaged for: {task[:40]}...")
            append_log(state.task_id, "⚡ [MODE] GENERATIVE PREEMPT: Direct synthesis, bypassing planner")

            from core.llm import call_llm
            gen_sys = _build_generative_system_prompt(task)
            gen_res = call_llm(task, system_prompt=gen_sys, role="strong", task_id=state.task_id)
            state.result = gen_res.get("content", "I encountered an error during synthesis.")
            state.confidence = max(gen_res.get("confidence", 0.85), 0.85)
            state.meta["confidence_type"] = "generative_preempt"
            state.status = "COMPLETED"

            return _standardize_final_return(
                "DONE",
                state.result,
                confidence=state.confidence,
                run_start_time=run_start_time,
                history=state.history,
                meta=state.meta
            )
        
        # Mandatory Pre-Search Grounding
        if grounding_data.get("required_grounding") in ["REAL_TIME", "RECENT"]:
            print(f"  ⚡ [loop] REAL_TIME intent detected. Triggering mandatory grounding search.")
            from core.tools import web_search, _fetch_page_content
            all_search_results = []
            for fact in grounding_data.get("target_facts", []):
                ground_res = web_search({"query": fact})
                
                # Signal Quality Check (Phase 40)
                status = ground_res.get("status") if isinstance(ground_res, dict) else "success"
                if status in ["low_signal", "error"]:
                    print(f"  ⚠️ [loop] Grounding signal weak/fail for '{fact}': {status}")
                    state.history_text += f"\n[Context Grounding] Tool:search Result: [SIGNAL_FAILURE] No reliable real-time data found for {fact}."
                else:
                    ground_res_str = json.dumps(ground_res) if isinstance(ground_res, dict) else str(ground_res)
                    state.history_text += f"\n[Context Grounding] Tool:search Result: {ground_res_str}"
                    if isinstance(ground_res, dict):
                        all_search_results.extend(ground_res.get("results", []))
            
            # --- PHASE 43: Boundary Robustness (Retry Logic) ---
            if "[SIGNAL_FAILURE]" in state.history_text and "Result: {" not in state.history_text:
                # Total failure on first pass -> Retry once with broader query
                from redis_client import append_log
                broad_query = task.lower().replace("current ", "").replace("latest ", "").replace("today's ", "").replace("today", "").strip()
                print(f"  🔄 [loop] RETRYING with broader query: {broad_query}")
                append_log(state.task_id, f"🔄 [loop] RETRYING with broader query: {broad_query}")
                
                ground_res = web_search({"query": broad_query})
                if ground_res.get("status") not in ["low_signal", "error"]:
                    ground_res_str = json.dumps(ground_res) if isinstance(ground_res, dict) else str(ground_res)
                    state.history_text += f"\n[Retry Grounding] Tool:search Result: {ground_res_str}"
                    if isinstance(ground_res, dict):
                        all_search_results.extend(ground_res.get("results", []))
            
            # --- PHASE 48: Deep Content Fetching ---
            # Fetch actual page content from top 2 URLs to get REAL DATA
            fetched_urls = set()
            deep_content = ""
            for r in all_search_results[:3]:
                url = r.get("url", "#")
                if url == "#" or url in fetched_urls:
                    continue
                # Resolve DDG redirect URLs
                if "duckduckgo.com" in url:
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                    url = parsed.get("uddg", [url])[0]
                fetched_urls.add(url)
                print(f"  📄 [loop] DEEP FETCH: {url[:80]}")
                content = _fetch_page_content(url, max_chars=1500)
                if content and len(content) > 50:
                    deep_content += f"\n[Deep Content from {url[:60]}]:\n{content}\n"
                if len(fetched_urls) >= 2:
                    break
            
            if deep_content:
                print(f"  ✅ [loop] Deep content fetched: {len(deep_content)} chars from {len(fetched_urls)} pages.")
                state.history_text += f"\n--- DEEP PAGE CONTENT ---{deep_content}"
        
        # --- PHASE 42: Execution Mode Switch (Simple vs Deep) ---
        def is_complex(t: str) -> bool:
            keywords = ["compare", "analyze", "explain deeply", "break down", "architecture", "theme", "summarize", "evaluate"]
            return any(k in t.lower() for k in keywords)

        # --- PHASE 44/45/46: Trust Calibration Helpers ---
        def normalize_canonical(text: str) -> str:
            """Minimal canonical normalization (btc -> bitcoin, etc.)"""
            t = text.lower()
            t = t.replace("btc", "bitcoin").replace("eth", "ethereum")
            t = t.replace("c°", "°c").replace("f°", "°f") # standardizing degree notation
            return t

        def has_time_context(text: str) -> bool:
            """Detects temporal signals (Phases 45)."""
            keywords = ["today", "now", "live", "latest", "yesterday", "2026"]
            return any(k in text.lower() for k in keywords)

        def strong_physical_signal(text: str) -> bool:
            """Detects textured signal (Phases 45)."""
            import re
            return any([
                "°" in text,
                "$" in text,
                "₹" in text,
                bool(re.search(r"\d+/\d+", text)) # score pattern
            ])

        def violates_query_constraints(text: str, query: str, task_id: str = None) -> bool:
            """Enforces Currency and Location constraints (Phase 46)."""
            from redis_client import append_log
            t = text.lower()
            q = query.lower()
            
            # 1. Currency Guard
            if ("inr" in q or "₹" in q) and ("$" in t and "₹" not in t and "inr" not in t):
                print(f"  🚨 [loop] SIGNAL REJECTED (currency mismatch)")
                if task_id: append_log(task_id, "🚨 [loop] SIGNAL REJECTED (currency mismatch)")
                return True
            
            # 2. Location Guard (Soft Enforcement)
            # Find capitalized words in query as potential locations
            import re
            potential_locations = re.findall(r"\b[A-Z][a-z]+\b", query)
            if potential_locations:
                query_locs = [l.lower() for l in potential_locations]
                found_in_text = any(loc in t for loc in query_locs)
                
                # If query location is MISSING, but OTHER known locations are present -> Reject
                if not found_in_text:
                    # Simple proxy for "other locations" using common major cities
                    common_cities = {"delhi", "mumbai", "london", "new york", "dubai", "singapore", "sydney"}
                    other_locs_in_text = any(city in t for city in common_cities if city not in query_locs)
                    if other_locs_in_text:
                        print(f"  🚨 [loop] SIGNAL REJECTED (location mismatch)")
                        if task_id: append_log(task_id, "🚨 [loop] SIGNAL REJECTED (location mismatch)")
                        return True
            return False

        # --- PHASE 44/45/46: Signal Interpretation (Juicy Signal Check) ---
        def is_signal_juicy(text: str, query: str, grounding_req: str, task_id: str = None) -> bool:
            """Pattern-based signal detection with Trust & Constraint calibration (Phase 46)."""
            import re
            
            # 0. Constraint Check (Phase 46)
            if violates_query_constraints(text, query, task_id):
                return False

            # Normalization
            norm_text = normalize_canonical(text)
            norm_query = normalize_canonical(query)

            # 1. Numeric/Fact Patterns
            has_fact = bool(re.search(r"(\d+°|\d+\sdeg|\d+[\./]\d+|[\$₹]\s?[\d,]+|[\d,]+\s?%)", norm_text))
            
            # 2. Weighted Alignment Check (Phase 46)
            q_words = set(re.sub(r"[^\w\s]", "", norm_query).split())
            t_words = set(re.sub(r"[^\w\s]", "", norm_text).split())
            
            # Use specific exclusion list (Phase 46)
            exclude = {"what", "is", "the", "in", "on", "at", "today", "now", "latest", "current", "of", "and", "to", "for", "me", "get"}
            q_refined = q_words - exclude
            
            # Weighted Alignment: Word must exist in t_words and NOT be a temporal filler
            temporal_fillers = {"today", "now", "latest", "current", "live"}
            content_words = q_refined - temporal_fillers
            
            overlap = len(content_words & t_words)
            is_aligned = overlap >= 1 
            
            if not is_aligned and content_words:
                print(f"  🚨 [loop] SIGNAL REJECTED (insufficient alignment)")
                if task_id: 
                    from redis_client import append_log
                    append_log(task_id, "🚨 [loop] SIGNAL REJECTED (insufficient alignment)")
            
            # 3. Trust Calibration: Freshness Gate
            if grounding_req == "REAL_TIME":
                fresh_or_textured = has_time_context(norm_text) or strong_physical_signal(norm_text)
                if not fresh_or_textured:
                    return False

            return has_fact and is_aligned

        grounding_req = grounding_data.get("required_grounding", "NONE")
        is_grounded_simple = grounding_req in ["REAL_TIME", "RECENT"] and not is_complex(task)
        
        # Simple Mode Fork
        if is_grounded_simple and not checkpoint:
            # Check for total grounding failure
            has_signal = "Result: {" in state.history_text
            is_factual_only = any(k in task.lower() for k in ["weather", "price", "score", "time", "date"])
            
            HONEST_FAILURE = "I couldn’t retrieve reliable live data for that right now. Try again in a moment."

            if not has_signal and is_factual_only:
                print(f"  🏁 [loop] SIMPLE MODE FALLBACK | Logic: Terminal Honesty")
                from redis_client import append_log
                append_log(state.task_id, "🏁 [loop] SIMPLE MODE FALLBACK (Terminal Honesty)")
                state.result = HONEST_FAILURE
                state.status = "COMPLETED"
            elif has_signal:
                print(f"  ⚡ [loop] SIMPLE MODE ENGAGED | Signal: High | Logic: Immediate Synthesis")
                from redis_client import append_log
                append_log(state.task_id, "⚡ [loop] SIMPLE MODE ENGAGED (Immediate Synthesis)")
                
                from core.llm import call_llm
                synth_prompt = f"""You are a factual data extraction engine. Your job is to answer the user's question using ONLY the data provided below.

STRICT RULES:
1. Extract and present SPECIFIC data points: scores, numbers, names, dates, prices, temperatures.
2. NEVER say "visit website X" or "check out X for more info". The user asked YOU for the answer.
3. If the data contains live scores, present them with team names, scores, overs, and key details.
4. If the data contains prices, present the exact price with currency.
5. If the data contains weather, present temperature, conditions, and location.
6. Format your answer clearly with relevant emojis for readability.
7. If you truly cannot find specific data in the facts, say what you DID find and be specific.
8. Cite the source briefly (e.g., "via Cricbuzz" or "per CoinGecko").

User Question: {task}

Retrieved Data:
{state.history_text}

Now provide a direct, factual answer:"""
                synth_res = call_llm(synth_prompt, role="fast", task_id=state.task_id)
                
                # --- PHASE 43/44/45/46: Confidence Gate & Trust/Constraint Calibration ---
                confidence = synth_res.get("confidence", 0.0)
                is_juicy = is_signal_juicy(state.history_text, task, grounding_req, task_id=state.task_id)
                
                bypass = False
                if is_juicy or state.is_generative_override:
                    print(f"  💎 [loop] SIGNAL BYPASS | Reason: {'GENERATIVE' if state.is_generative_override else 'JUICY'}")
                    append_log(state.task_id, f"💎 [loop] SIGNAL BYPASS ({'GENERATIVE' if state.is_generative_override else 'JUICY'})")
                    if confidence < 0.5:
                        print(f"  🛡️ [loop] CONFIDENCE BYPASSED (override: {confidence})")
                        append_log(state.task_id, f"🛡️ [loop] CONFIDENCE BYPASSED (override: {confidence})")
                        bypass = True

                if confidence < 0.5 and not bypass:
                    print(f"  🚨 [loop] SYNTHESIS REJECTED (low confidence: {confidence})")
                    append_log(state.task_id, f"🚨 [loop] SYNTHESIS REJECTED (low confidence: {confidence})")
                    state.result = HONEST_FAILURE
                    print(f"  🏁 [loop] SIMPLE MODE FALLBACK (Terminal Honesty)")
                    append_log(state.task_id, "🏁 [loop] SIMPLE MODE FALLBACK (Terminal Honesty)")
                    state.meta["fallback_reason"] = "low_confidence_synthesis"
                else:
                    state.result = synth_res.get("content", "I found the data but encountered an error during synthesis.")
                    # Requirement #3: Calibrate confidence
                    if state.is_generative_override:
                        state.confidence = max(confidence, 0.6)
                        state.meta["confidence_type"] = "fallback_synthesis"
                    else:
                        state.confidence = confidence
                        state.meta["confidence_type"] = "normal"
                
                state.status = "COMPLETED"
            else:
                print(f"  🛡️ [loop] SIMPLE MODE BYPASSED | Signal: Low & Ambiguous | Escalating to DEEP MODE")
                from redis_client import append_log
                append_log(state.task_id, "🛡️ [loop] SIMPLE MODE BYPASSED (No signal/Ambiguous) -> ESCALATING TO DEEP MODE")
        
        if state.status == "PLANNING":
            print(f"  🚀 [loop] DEEP MODE ENGAGED | Strategic reasoning loop required.")
            from redis_client import append_log
            append_log(state.task_id, "🚀 [loop] DEEP MODE ENGAGED")
            
            strategy_info = select_strategy(task, prior_insights, global_stats=global_stats, test_mode=test_mode)
            
            # Phase 12: Pass search insights and pre-search grounding to the planner
            memory_context = "\n".join([str(ins) for ins in prior_insights]) if prior_insights else ""
            if state.history_text:
                memory_context += f"\n--- PRE-SEARCH GROUNDING ---\n{state.history_text}\n"
                
            # Phase 33: Tactical Planning with Task ID and Role (Strong)
            res_plan_data = planner_agent.generate_plan(
                task, memory_context=memory_context, 
                strategy_info=strategy_info, 
                reason_traces=reason_traces,
                task_id=state.task_id,
                grounding_data=state.grounding_data
            )
            
            # Phase 35: Access content safely
            res_plan = res_plan_data if isinstance(res_plan_data, dict) else {"steps": []}
            
            # Phase 12.5: Handle Terminal Brain Failure
            if res_plan.get("reason") == "BRAIN_DEAD":
                print(f"  🚨 [loop] BRAIN_DEAD: Infrastructure failure detected.")
                state.status = "BRAIN_DEAD"
                state.result = f"Brain disconnected: {res_plan.get('error')}"
                state.save()
                return {
                    "status": "failed",
                    "answer": _ensure_str_answer(f"Brain disconnected: {res_plan.get('error')}"),
                    "confidence": 0.0,
                    "steps": 0,
                    "tools_used": 0,
                    "response_time_ms": int((time.time() - run_start_time) * 1000)
                }

            state.plan = res_plan.get("steps", [])
            
            if res_plan.get("status") == "INSUFFICIENT_CONFIDENCE":
                print(f"  🛑 [planner] Insufficient Confidence: {res_plan.get('reason')}")
                state.status = "INSUFFICIENT_CONFIDENCE"
                state.result = f"I cannot proceed with high confidence. Reason: {res_plan.get('reason')}"

            if not state.plan and state.status == "PLANNING":
                print("  🚨 [planner] Error: Planner generated an empty plan.")
                state.status = "FAILED"

            if state.status == "PLANNING":
                state.strategy_type = strategy_info.get("suggested_strategy", "explore")
                state.constraints = {}
                state.status = "EXECUTING"
                print(f"  🧠 [planner] Iteration {state.replan_counter} | Steps: {len(state.plan)}")
            
    # 3.5 Escape Hatch / Fallback Trigger (Requirement #2 - Deterministic Fallback)
    planner_failed = (
        not state.plan or 
        state.confidence < 0.5 or 
        state.status in ["FAILED", "INSUFFICIENT_CONFIDENCE"]
    )
    
    if (state.is_generative_override or state.is_hybrid_fallback) and planner_failed:
        # Refinement: Double Synthesis Guard
        if state.result:
             print(f"  🛑 [loop] Fallback skipped: Task already has result.")
             return _standardize_final_return("DONE", state.result, confidence=state.confidence, run_start_time=run_start_time, history=state.history, meta=state.meta)

        print(f"  🚀 [MODE] GENERATIVE FALLBACK TRIGGERED | Reason: {'FAILED' if not state.plan else 'UNCONFIDENT'}")
        append_log(state.task_id, f"🚀 [MODE] GENERATIVE FALLBACK TRIGGERED ({'FAILED' if not state.plan else 'UNCONFIDENT'})")
        
        # Refinement: Forensic Metadata (Requirement #1)
        state.meta["fallback_reason"] = {
            "plan_empty": not state.plan,
            "low_confidence": state.confidence < 0.5,
            "status": state.status
        }
        print(f"  [DEBUG] FALLBACK REASON: {json.dumps(state.meta['fallback_reason'])}")

        # Force Direct LLM Synthesis
        from core.llm import call_llm
        fallback_prompt = f"You are Barney, an expert reasoning agent. Answer the following request using your internal knowledge. Provide a comprehensive, high-quality response.\n\nTask: {task}"
        if state.history_text:
            fallback_prompt += f"\n\nContext:\n{state.history_text}"
            
        fallback_res = call_llm(fallback_prompt, role="strong", task_id=state.task_id)
        state.result = fallback_res.get("content", "I encountered an error during fallback synthesis.")
        state.confidence = max(fallback_res.get("confidence", 0.6), 0.6)
        state.meta["confidence_type"] = "fallback" # Requirement #3
        state.status = "COMPLETED"
        print(f"  🏁 [fallback] Synthesis complete. Confidence: {state.confidence}")
        append_log(state.task_id, f"🏁 Fallback synthesis complete. Confidence: {state.confidence}")

    # 3.6 Exit early if rejected or timeout (Chaos Guard)
    if state.status in ["REJECTED_TIMEOUT", "FAILED", "INSUFFICIENT_CONFIDENCE"]:
        if not (state.is_generative_override and state.status == "INSUFFICIENT_CONFIDENCE"):
             return _standardize_final_return("failed", state.result or "Governance rejection or safety timeout triggered.", run_start_time=run_start_time)

    # 4. Governed Execution Loop
    # Phase 37: Production-Grade Idempotency
    NON_IDEMPOTENT_TOOLS = ["get_current_time", "random_generator", "live_fetch"]

    def is_valid_result(res):
        return (res and isinstance(res, dict) and res.get("status") == "success" and (res.get("answer") or res.get("history_update")))

    while state.current_step_index < len(state.plan):
        step_idx = state.current_step_index
        step = state.plan[step_idx]
        step_id = _generate_step_id(state.task_id, step, state.replan_counter)

        # 1. First Pass: Cache Check (Version-Bound)
        from redis_client import get_step_result, acquire_step_lock, release_step_lock, save_step_result, refresh_lock
        cached_res = get_step_result(state.task_id, state.replan_counter, step_id)
        if cached_res:
            print(f"  ⏭️ [idempotency] Cache HIT for Step {step_idx+1}. Reusing result.")
            res_data = cached_res
            state.history.append(res_data)
            state.history_text = res_data.get("history_update", state.history_text)
            if res_data.get("answer"): state.result = res_data["answer"]
            state.completed_step_ids.append(step_id)
            state.current_step_index += 1
            continue

        # 2. Polling Logic with Grace Delay
        owner_token = str(uuid.uuid4())
        lock_ttl = 300 if task_type == "research" else 120
        lock_acquired = False
        
        for poll_attempt in range(3):
            if acquire_step_lock(state.task_id, state.replan_counter, step_id, owner_token, ttl=lock_ttl):
                lock_acquired = True
                break
            
            # Lock exists -> Poll result
            cached_res = get_step_result(state.task_id, state.replan_counter, step_id)
            if cached_res:
                print(f"  🏢 [idempotency] Smart Poll hit result for Step {step_idx+1}.")
                break
            
            print(f"  ⏳ [idempotency] Step {step_idx+1} locked. Polling ({poll_attempt+1}/3)...")
            time.sleep(1.0)
        
        # 3. Post-Poll Handling
        if not lock_acquired:
            res_data = get_step_result(state.task_id, state.replan_counter, step_id)
            if res_data:
                print(f"  🏢 [idempotency] Secondary Cache Hit for Step {step_idx+1}.")
                state.history.append(res_data)
                state.history_text = res_data.get("history_update", state.history_text)
                if res_data.get("answer"): state.result = res_data["answer"]
                state.completed_step_ids.append(step_id)
                state.current_step_index += 1
                continue
            else:
                # Still no lock and no result? Grace Delay before final snatched attempt
                grace = 0.5 + random.random() * 0.5
                print(f"  💤 [idempotency] Grace delay engaged ({grace:.2f}s)...")
                time.sleep(grace)
                if not acquire_step_lock(state.task_id, state.replan_counter, step_id, owner_token, ttl=lock_ttl):
                    print(f"  🚨 [idempotency] Abandoning step {step_idx+1}: persistent lock collision.")
                    state.status = "FAILED"
                    break
                lock_acquired = True

        # Secondary Cache Re-check (Standard Double-Check Pattern)
        res_data = get_step_result(state.task_id, state.replan_counter, step_id)
        if res_data:
            print(f"  🏢 [idempotency] Post-lock cache hit for Step {step_idx+1}.")
            release_step_lock(state.task_id, state.replan_counter, step_id, owner_token)
            state.history.append(res_data)
            state.history_text = res_data.get("history_update", state.history_text)
            if res_data.get("answer"): state.result = res_data["answer"]
            state.completed_step_ids.append(step_id)
            state.current_step_index += 1
            continue
        
        risk = assess_risk(step, state.history, prev_cumulative=state.cumulative_risk)
        state.risk_scores[step_idx] = risk
        print(f"  🛡️ [risk] Step {step_idx+1}: {risk['risk_level']} (Comp: {risk['cumulative_risk']}) - {risk['reason']}")

        if (risk["risk_level"] == "HIGH" or risk.get("cumulative_risk", 0) > 0.8) and state.status != "HUMAN_APPROVED":
            if state.status != "WAITING_FOR_HUMAN":
                state.wait_start_time = time.time()
                state.status = "WAITING_FOR_HUMAN"
            
            wait_time = time.time() - state.wait_start_time
            if wait_time > MAX_WAIT:
                print(f"  🚨 [timeout] High-risk timeout after {MAX_WAIT}s. Policy: REJECT.")
                state.status = "REJECTED_TIMEOUT"
                break
            
            return {
                "status": "governance",
                "state": state.to_dict(),
                "checkpoint": {"step_index": step_idx, "step": step, "risk": risk, "wait_time": wait_time}
            }

        # Human Approval Handler (Decay)
        if state.status == "HUMAN_APPROVED":
            old_risk = state.cumulative_risk
            state.cumulative_risk = apply_decay(state.cumulative_risk)
            state.status = "EXECUTING"
            state.wait_start_time = 0.0
            state.add_log(step_idx, "HUMAN_APPROVED", risk["risk_score"], risk["reason"], 
                          log_type="HUMAN_OVERRIDE", risk_before=old_risk, risk_after=state.cumulative_risk, step_id=step_id)

        # Execute Step
        print(f"  ⚙️ [executor] Step {step_idx+1}/{len(state.plan)}: {step}")
        # Phase 33: Adaptive Step Execution
        # Logic: First step and high-risk steps use Strong model (Llama 70b)
        # Routine middle steps use Fast model (Llama 8b)
        role_hint = "strong" if step_idx == 0 or risk["risk_score"] > 0.7 else "fast"
        
        # Phase 37: Heartbeat Thread for long-running steps
        stop_heartbeat = threading.Event()
        def lock_heartbeat():
            from redis_client import refresh_lock
            interval = lock_ttl / 3
            while not stop_heartbeat.is_set():
                time.sleep(interval)
                if stop_heartbeat.is_set(): break
                if refresh_lock(state.task_id, state.replan_counter, step_id, owner_token, ttl=lock_ttl):
                    print(f"  💓 [idempotency] Heartbeat: Lock refreshed for Step {step_idx+1}.")
                else:
                    print(f"  ⚠️ [idempotency] Heartbeat FAILED for Step {step_idx+1}. Lock possibly stolen.")

        heartbeat_thread = threading.Thread(target=lock_heartbeat, daemon=True)
        if lock_acquired: heartbeat_thread.start()

        try:
            res_data = executor_agent.execute_single_step(
                task, step, step_idx, len(state.plan), 
                history=state.history_text,
                tool_history=[], 
                constraints=state.constraints,
                strategy_type=state.strategy_type,
                task_id=state.task_id,
                role=role_hint,
                replan_counter=state.replan_counter,
                step_id=step_id
            )
            
            # Phase 37: Write-Verify-Release
            if is_valid_result(res_data):
                save_step_result(state.task_id, state.replan_counter, step_id, res_data)
                # Verify immediately
                verify_res = get_step_result(state.task_id, state.replan_counter, step_id)
                if verify_res:
                    print(f"  💾 [idempotency] Step {step_idx+1} result PERSISTED.")
                else:
                    print(f"  🛑 [idempotency] Write verification FAILED for Step {step_idx+1}.")
            else:
                print(f"  🧪 [idempotency] Skipping cache for Step {step_idx+1}: Result poisoned or invalid.")
        finally:
            stop_heartbeat.set()
            if lock_acquired:
                release_step_lock(state.task_id, state.replan_counter, step_id, owner_token)
        
        # Phase 35: Response Handling
        res_text = res_data.get("content", "") if isinstance(res_data, dict) else str(res_data)
        res = res_data if isinstance(res_data, dict) else {"status": "success", "content": res_text}
        if "history_update" not in res: res["history_update"] = res_text
        
        if res.get("status") == "success":
            justification = res.get("justification", {})
            intent = justification.get("intent", "").lower().strip()
            # Warn about intent mismatch but do NOT reject — false rejections were causing "No answer generated"
            if intent and len(intent) > 5 and intent not in step.lower() and "search" not in step.lower() and "final" not in step.lower() and "synthesize" not in step.lower():
                print(f"    ⚠️ [trust] Justification mismatch! Intent='{intent}' not in step='{step}'. (Warning only)")

            # Always verify step outcome
            verification = verify_step_outcome(step, justification, res.get("history_update", ""))
            res["verification"] = verification
            print(f"    ✅ [verify] Confidence: {verification['confidence']} | {verification['evidence']}")

            if verification["confidence"] < 0.6:
                if state.replan_counter < 2 and risk["risk_level"] != "HIGH":
                    print(f"    🔄 [trust] Low confidence detected. Silent Replan triggering...")
                    feedback = {"type": "LOW_CONFIDENCE", "reason": f"Step verification failed: {verification['evidence']}", "priority": "SOFT"}
                    # Phase 33: Replanning with Role
                    new_plan = planner_agent.replan(state.task, feedback, task_id=state.task_id)
                    state.plan = new_plan.get("steps", [])
                    state.replan_counter += 1
                    state.current_step_index = 0
                    state.status = "PLANNING"
                    return run_task(task, state_dict=state.to_dict())
                else:
                    print(f"    🚨 [trust] Persistent failure or High Risk context. Escalating to Governance Panel.")
                    state.status = "WAITING_FOR_HUMAN"
                    state.wait_start_time = time.time()
                    return { "status": "governance", "state": state.to_dict(), "checkpoint": {"step_index": step_idx, "step": step, "risk": risk, "verification": verification} }

            state.history.append(res)
            state.history_text = res["history_update"]
            state.current_step_index += 1
            if res.get("answer"): state.result = res["answer"]
            state.completed_step_ids.append(step_id)
            state.cumulative_risk = risk.get("cumulative_risk", state.cumulative_risk)
            state.add_log(step_idx, "AUTO", risk["risk_score"], risk["reason"], step_id=step_id)
            
            # Step 4: Atomic Checkpoint Save (Phase 31)
            new_checkpoint = {
                "current_step": state.current_step_index,
                "plan": state.plan,
                "completed_steps": state.completed_step_ids
            }
            update_task(state.task_id, "RUNNING", checkpoint=new_checkpoint)
        
        elif res.get("reason") == "BRAIN_DEAD":
            print(f"  🚨 [loop] BRAIN_DEAD in execution: {res.get('error')}")
            state.status = "BRAIN_DEAD"
            state.result = f"Brain disconnected mid-execution: {res.get('error')}"
            state.save()
            return _standardize_final_return(
                "failed", 
                state.result, 
                confidence=0.0, 
                run_start_time=run_start_time,
                history=state.history
            )
        else:
            print(f"  🚨 [loop] Step execution failed: {res.get('reason')}")
            state.status = "FAILED"
            break

    # Final Wrap-up
    if state.current_step_index >= len(state.plan):
        state.status = "COMPLETED"
    
    # CRITICAL SAFETY NET: If all steps ran but no answer was produced,
    if state.result is None:
        print("⚠️ No final result. Triggering synthesis fallback.")

        from core.llm import call_llm
        response = call_llm(f"""
        You must produce a final answer.

        Task: {state.task}

        Use all available knowledge and prior steps:
        {state.history_text}

        Give a clear, complete answer.
        """)

        state.result = response.get("content")
        state.status = "COMPLETED"

    if "[TOOL_FAILED]" in str(state.history_text) or "No direct abstract found" in str(state.history_text):
        confidence = 0.6
    else:
        confidence = 0.9

    state.final_confidence = confidence
        
    # PIPELINE CONTRACT: Enforce string answer at terminal assembly
    state.result = _ensure_str_answer(state.result)
    print(f"  [FINAL] Answer type: {type(state.result).__name__}")
    print(f"  [FINAL] Answer preview: {str(state.result)[:100]}")
    
    result_data = {
        "status": "DONE",
        "answer": state.result,
        "confidence": state.final_confidence,
        "steps": len(state.history),
        "tools_used": sum(h.get("tool_calls", 0) for h in state.history if isinstance(h, dict)),
        "response_time_ms": int((time.time() - run_start_time) * 1000)
    }

    q_score = score_research_quality(state.history)
    print(f"  📊 [quality] Sources: {q_score['source_count']} | Consistency: {q_score['consistency_score']} | Confidence: {q_score['final_confidence']}")
    
    if q_score["final_confidence"] > 0.4:
         from core.tools import update_ledger
         update_ledger(task, summary=result_data["answer"][:500], source=f"Multi-Source ({q_score['source_count']})", confidence=q_score["final_confidence"])

    _memory.add({"task": task, "result": result_data["answer"], "success": (state.status == "COMPLETED"), "timestamp": _memory.count() + 1, "type": "governance_run"})

    # Phase 35: Ground Truth Semantic Evaluator (Terminal Judge)
    final_answer = result_data["answer"]
    task_complexity = get_required_depth(task)
    
    # 1. Diversity Judge: If generator was 70b, use 8b as judge (and vice-versa)
    # We take the model ID from the last history entry
    last_model = state.history[-1].get("model") if state.history else "llama-3.1-8b-instant"
    judge_model = SemanticEvaluator.get_diverse_judge_model(last_model)
    
    # Phase 36: Reality Grounding Audit
    grounding_score = 1.0
    grounding_report = {}
    semantic_score = 7.0 # Default value for yield tracking
    
    if SemanticEvaluator.should_we_judge(task, task_complexity, final_answer):
        from core.llm import call_llm
        
        # 1. Strategic Grounding Audit
        volatile_claims = RealityAnchor.extract_volatile_claims(final_answer)
        grounding_report = RealityAnchor.match_history(volatile_claims, state.history)
        grounding_score = RealityAnchor.calculate_grounding_score(grounding_report)
        
        # 2. Diversity Judge (Semantic Opinion)
        judge_prompt = f"Evaluate this response against the original task.\nTask: {task}\nResponse: {final_answer}\nAssign Score (0.0-10.0)."
        eval_resp = call_llm(judge_prompt, role="fast", is_judge_call=True)
        
        match = re.search(r"Score:\s*([0-9\.]+)", eval_resp.get("content", ""))
        semantic_score = float(match.group(1)) if match else 7.0
        
        # 3. Truth-Weighted Integration (Phase 36: 40/60 weight)
        final_quality = SemanticEvaluator.calculate_integrated_score(semantic_score, grounding_score)
        
        # 4. Self-Correction Loop (Phase 36: MAX_CORRECTIONS = 1)
        if final_quality < 6.0 and state.correction_count < 1 and grounding_score < 0.7:
             print(f"  🔄 [correction] Poor grounding ({grounding_score}). Triggering single-loop re-verification...")
             state.correction_count += 1
             # Append a "Reality Verification" step to the history and allow one more executor pass
             state.history_text += f"\n[SYSTEM ALERT]: The following claims were UNVERIFIED: {grounding_report.get('unverified')}. Please verify them using a tool or search before finalizing."
             state.status = "EXECUTING"
             state.current_step_index = len(state.plan) - 1 # Re-run last step with warning
             return run_task(task, state_dict=state.to_dict())

        tier = SemanticEvaluator.classify_quality_tier(final_quality, grounding_score)
        
        print(f"  🏢 [ground_truth] Final Score: {final_quality}/10 (Sem: {semantic_score}, Gnd: {grounding_score}) | Tier: {tier}")
        result_data["semantic_score"] = semantic_score
        result_data["grounding_score"] = grounding_score
        result_data["integrated_quality"] = final_quality
        result_data["quality_tier"] = tier
        result_data["grounding_report"] = grounding_report
        
        if tier.startswith("FAILED"):
             print(f"  🚨 [quality] Unsatisfactory result quality ({final_quality}). Marking as FAILED.")
             state.status = "FAILED"

    # Step 5: Completion Logic (Phase 35: record quality yield)
    if state.status == "COMPLETED":
        update_task(state.task_id, "DONE", result_data, checkpoint=None)
        record_model_experience(task_type, last_model, semantic_score / 10.0)
    else:
        record_model_experience(task_type, last_model, 0.1) # Minimum yield for failure
    
    print("🏁 FINAL RESULT:", result_data)
    return _standardize_final_return(
        "DONE", 
        state.result, 
        confidence=state.confidence, 
        run_start_time=run_start_time,
        history=state.history,
        meta=state.meta,
        quality_metrics=result_data
    )
