import subprocess
import sys
import re
import tempfile
import os
from core.llm import call_llm

def _extract_code(text: str) -> str:
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    if "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

def detect_required_credentials(task: str) -> dict:
    """
    Ask LLM whether this task needs an external API and what credentials are required.
    Returns dict: { needs_api: bool, api_name: str, credential_token: str, install_package: str }
    """
    prompt = f"""You are analyzing whether a task requires calling an external API to get real-time or live data.

Task: {task}

External APIs are needed for:
- Weather (current conditions, temperature, forecast)
- Stock prices, crypto prices
- News headlines
- Sports scores
- Currency exchange rates
- Any live/real-time data

Reply with JSON only:
{{
  "needs_api": true or false,
  "api_name": "name of the API (e.g. OpenWeatherMap, NewsAPI, CoinGecko)",
  "credential_token": "token name for the key (e.g. OPENWEATHER_API_KEY)",
  "install_package": "pip package name (use 'requests' for most APIs)",
  "reasoning": "one sentence why"
}}

For weather tasks, needs_api is ALWAYS true and api_name is OpenWeatherMap."""

    res = call_llm(prompt, role="fast")
    content = res.get("content", "{}")

    import json
    try:
        clean = content.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()
        return json.loads(clean)
    except Exception:
        return {"needs_api": False, "api_name": "", "credential_token": "", "install_package": ""}


def build_and_run_tool(task: str, credentials: dict) -> str:
    """
    Ask LLM to write Python code for the task, inject credentials, run via subprocess.
    Returns the output string.
    """
    cred_description = "\n".join([f"- {k} = {v}" for k, v in credentials.items()])

    prompt = f"""Write a complete Python script to accomplish this task: {task}

Available credentials (already assigned as variables at the top of the script):
{cred_description}

Requirements:
1. Start the script by assigning the credentials as variables exactly as listed above.
2. Use the requests library for any HTTP calls (prefer requests over SDK libraries).
3. Print the final answer clearly at the end with a line starting: BARNEY_RESULT:
4. Handle exceptions and print: BARNEY_ERROR: <reason> if something fails.
5. Keep it simple and self-contained. No input() calls. No user prompts.
6. Return only the Python code, no explanation."""

    res = call_llm(prompt, role="strong")
    code = _extract_code(res.get("content", ""))

    if not code:
        return "Failed to generate tool code."

    # Inject credentials as literal assignments at the top (safety override)
    cred_lines = "\n".join([f'{k} = """{v}"""' for k, v in credentials.items()])
    final_code = f"{cred_lines}\n\n{code}"

    # Install required packages first
    packages_prompt = f"List only the pip package names needed for this code, one per line, nothing else:\n\n{code}"
    pkg_res = call_llm(packages_prompt, role="fast")
    packages = [
        p.strip() for p in pkg_res.get("content", "").strip().splitlines()
        if p.strip() and not p.strip().startswith("#")
    ]
    for pkg in packages[:5]:  # safety limit
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                timeout=30, capture_output=True
            )
        except Exception:
            pass

    # Write to temp file and run
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(final_code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr

        if "BARNEY_RESULT:" in output:
            answer = output.split("BARNEY_RESULT:")[-1].strip()
            return answer
        elif "BARNEY_ERROR:" in output:
            return f"Tool error: {output.split('BARNEY_ERROR:')[-1].strip()}"
        elif output.strip():
            return output.strip()
        else:
            return "Tool ran but produced no output."
    except subprocess.TimeoutExpired:
        return "Tool execution timed out after 30 seconds."
    except Exception as e:
        return f"Tool execution failed: {str(e)}"
    finally:
        os.unlink(tmp_path)
