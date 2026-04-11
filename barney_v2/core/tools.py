import os
import requests
import json
import time
import tempfile
import shutil
import hashlib
from duckduckgo_search import DDGS

DATA_ROOT = "barney_data"
BACKUP_ROOT = os.path.join(DATA_ROOT, ".backups")
MAX_BACKUPS = 5

def _secure_path(filename: str) -> str:
    """Sandbox enforcement: Ensures files are inside barney_data."""
    # Block path traversal
    if ".." in filename or filename.startswith("/"):
        raise PermissionError(f"Access denied: Path '{filename}' is outside sandbox.")
    return os.path.join(DATA_ROOT, filename)

def _update_manifest(filename: str, action: str, size: int = 0, intent: str = "Unknown"):
    """Atomic Manifest Update: Tracks file lifecycle with 'Intent'."""
    manifest_path = _secure_path("manifest.json")
    
    # 1. Load existing
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except: manifest = []

    # 2. Add entry
    entry = {
        "file": filename,
        "action": action,
        "size": size,
        "intent": intent,
        "timestamp": time.time_ns()
    }
    manifest.append(entry)
    # Keep last 100 entries
    manifest = manifest[-100:]

    # 3. Atomic Write
    fd, temp_path = tempfile.mkstemp(dir=DATA_ROOT)
    with os.fdopen(fd, 'w') as f:
        json.dump(manifest, f, indent=2)
    os.replace(temp_path, manifest_path)

def summarize_ledger():
    """Adaptive Intelligence: Self-Cleaning & Compression (Phase 12)."""
    ledger_path = _secure_path("knowledge_ledger.json")
    if not os.path.exists(ledger_path): return
    
    with open(ledger_path, 'r') as f:
        ledger = json.load(f)
    
    if len(ledger) < 2: return

    print(f"  🧹 [memory] Compressing ledger ({len(ledger)} entries)...")
    
    # 1. Load LLM to merge redundant tasks
    from core.llm import call_llm
    
    # Prune oldest if we hit the actual limit for simulation, 
    # but the goal is to merge.
    # To avoid huge LLM calls, we pick the most redundant-looking 20 entries.
    ledger.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    compressed = ledger[:25] # Preserve top 25 high-confidence
    
    fd, temp_path = tempfile.mkstemp(dir=DATA_ROOT)
    with os.fdopen(fd, 'w') as f:
        json.dump(compressed, f, indent=2)
    os.replace(temp_path, ledger_path)
    _update_manifest("knowledge_ledger.json", "LEDGER_COMPRESSION", intent="Pruning low-value data to prevent noise explosion")

def update_ledger(task: str, summary: str, source: str = "Search", confidence: float = 0.7, file_ref: str = None):
    """Trust Layer: Confidence-Aware Knowledge Persistence (Phase 11.5)."""
    ledger_path = _secure_path("knowledge_ledger.json")
    
    # 1. Load existing
    ledger = []
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, 'r') as f:
                ledger = json.load(f)
        except: ledger = []

    # 2. Conflict Detection (Light)
    new_norm = str(summary).lower()[:50]
    for entry in ledger:
        old_norm = str(entry.get("summary", "")).lower()[:50]
        if entry.get("task") == task and old_norm != new_norm:
            entry["status"] = "CONFLICTED"
            # Rule: Confidence never increases on conflict
            entry["confidence"] = min(entry.get("confidence", 0.7), 0.3)
            entry["notes"] = f"Contradicted by {source} data."

    # 3. Add entry
    from core.memory_embeddings import embed_text
    entry_embedding = embed_text(summary)
    
    entry = {
        "id": hashlib.md5(f"{task}{time.time_ns()}".encode()).hexdigest()[:8],
        "task": task,
        "summary": summary,
        "source": source,
        "confidence": confidence,
        "embedding": entry_embedding, # Semantic Vector (Fix #1)
        "status": "VERIFIED" if confidence > 0.8 else "PROVISIONAL",
        "last_verified": time.time_ns(),
        "file_ref": file_ref,
        "timestamp": time.time_ns()
    }
    ledger.append(entry)
    
    # 3.5 Memory Volume Control: 100 entry limit (Phase 25 Step 7)
    if len(ledger) > 100:
        ledger.sort(key=lambda x: x.get("timestamp", 0))
        ledger = ledger[-100:]

    # 4. Atomic Write
    fd, temp_path = tempfile.mkstemp(dir=DATA_ROOT)
    with os.fdopen(fd, 'w') as f:
        json.dump(ledger, f, indent=2)
    os.replace(temp_path, ledger_path)

    # 5. Conditional Compression (Phase 12)
    if len(ledger) > 50:
        summarize_ledger()
        
    _update_manifest("knowledge_ledger.json", "LEDGER_UPDATE", size=len(summary), intent=f"Persisting verified insight: {task}")
    return f"Success: Knowledge Ledger updated with {confidence*100}% confidence."

def _backup_file(filename: str):
    """Versioning Policy: Keeps last 5 versions of a file."""
    source_path = _secure_path(filename)
    if not os.path.exists(source_path):
        return

    os.makedirs(BACKUP_ROOT, exist_ok=True)
    
    # 1. Create Timestamped Backup
    ts = time.time_ns()
    backup_name = f"{filename}_{ts}.bak"
    backup_path = os.path.join(BACKUP_ROOT, backup_name)
    shutil.copy2(source_path, backup_path)

    # 2. Prune Oldest
    all_backups = [f for f in os.listdir(BACKUP_ROOT) if f.startswith(f"{filename}_")]
    # Sort by timestamp in name
    all_backups.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    while len(all_backups) > MAX_BACKUPS:
        oldest = all_backups.pop(0)
        os.remove(os.path.join(BACKUP_ROOT, oldest))

def list_dir(path: str = ".") -> str:
    """Explore: List contents of the sandboxed data directory."""
    try:
        target = _secure_path(path)
        if not os.path.exists(target):
            return f"Error: Path '{path}' does not exist."
        files = os.listdir(target)
        _update_manifest(path, "LIST", intent="Exploring directory structure")
        return f"Files in {path}: " + ", ".join(files)
    except Exception as e:
        return f"List Error: {str(e)}"

def read_file(filename: str) -> str:
    """Read: Extract text content from a sandboxed file."""
    try:
        target = _secure_path(filename)
        with open(target, 'r') as f:
            content = f.read()
            _update_manifest(filename, "READ", size=len(content), intent="Accessing data for reasoning")
            return content[:2000] 
    except Exception as e:
        return f"Read Error: {str(e)}"

def write_file(filename_or_dict: str, content: str = None) -> str:
    """Action: Atomic Save with Automatic Versioning."""
    try:
        intent = "Direct write (no specified intent)"
        if isinstance(filename_or_dict, dict):
            filename = filename_or_dict.get("filename")
            content = filename_or_dict.get("content")
            intent = filename_or_dict.get("intent", "Structured tool action")
        elif isinstance(filename_or_dict, str) and content is None:
            if "," in filename_or_dict:
                parts = filename_or_dict.split(",", 1)
                filename = parts[0].strip()
                content = parts[1].strip()
            else:
                filename = filename_or_dict
                content = ""
        else:
            filename = filename_or_dict

        if not filename:
            return "Error: write_file requires a 'filename'."

        target = _secure_path(filename)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        
        # 1. Backup if exists
        _backup_file(filename)

        # 2. Atomic Write
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(target))
        with os.fdopen(fd, 'w') as f:
            f.write(content if content is not None else "")
        os.replace(temp_path, target)

        _update_manifest(filename, "WRITE", size=len(content) if content else 0, intent=intent)
        return f"Success: Saved {len(content) if content else 0} bytes to {filename}"
        
    except PermissionError as pe:
        raise pe
    except Exception as e:
        return f"Write Error: {str(e)}"

def http_fetch(input_data: dict) -> str:
    """Sanitized HTTP fetch tool with timeout and truncation."""
    url = input_data.get("url")
    if not url:
        return "Error: No URL provided."
    
    # Safety: Block local access
    if any(local in url.lower() for local in ["localhost", "127.0.0.1", "0.0.0.0"]):
        return "Access Error: Forbidden address detected (Localhost/Internal)."

    try:
        res = requests.get(url, timeout=5)
        return res.text[:1000]
    except Exception as e:
        return f"Fetch Error: {str(e)}"

def run_python(input_data: dict) -> dict:
    """Hardened Python execution with restricted globals and math support."""
    code = input_data.get("code", "")
    if not code:
        return {"error": "No code provided."}

    # Strict Security Filter
    FORBIDDEN = ["import", "__", "open", "exec", "eval", "os", "sys"]
    for word in FORBIDDEN:
        if word in code:
            return {"error": f"Forbidden operation detected: '{word}'"}

    import math
    local_env = {}
    allowed_globals = {
        "__builtins__": {},
        "math": math
    }

    try:
        exec(code, allowed_globals, local_env)
        # Convert local_env to string-safe dict for LLM
        return {"output": {k: str(v) for k, v in local_env.items()}}
    except Exception as e:
        return {"error": str(e)}

def get_current_time(input_data: dict = None) -> str:
    """Simple temporal awareness tool."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _scrape_ddg(query: str, headers: dict) -> list:
    """Scrape DuckDuckGo HTML search."""
    from bs4 import BeautifulSoup
    url = f"https://html.duckduckgo.com/html/?q={query}"
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    
    raw_results = soup.select(".result")
    formatted = []
    for r in raw_results[:5]:
        title_tag = r.select_one(".result__a")
        snippet_tag = r.select_one(".result__snippet")
        snippet = ""
        if snippet_tag:
            snippet = snippet_tag.text
        else:
            body = r.select_one(".result__body")
            if body:
                snippet = body.text
        snippet = " ".join(snippet.split())
        title = " ".join(title_tag.text.split()) if title_tag else "Unknown"
        href = title_tag["href"] if title_tag and title_tag.has_attr("href") else "#"
        if title and snippet:
            formatted.append({"title": title, "snippet": snippet, "url": href})
    return formatted

def _scrape_brave(query: str, headers: dict) -> list:
    """Fallback: Scrape Brave Search results (Phase 47)."""
    from bs4 import BeautifulSoup
    import urllib.parse
    url = f"https://search.brave.com/search?q={urllib.parse.quote_plus(query)}"
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    
    formatted = []
    
    # 1. News Carousel (enrichment-card-item) — richest data for live/news queries
    for card in soup.select("a.enrichment-card-item")[:5]:
        title_el = card.select_one("div.desktop-small-semibold")
        site_el = card.select_one("div.enrichment-card-site")
        time_el = card.select_one("div.enrichment-card-metadata")
        href = card["href"] if card.has_attr("href") else "#"
        
        title = " ".join(title_el.get_text().split()) if title_el else ""
        site = " ".join(site_el.get_text().split()) if site_el else ""
        time_str = " ".join(time_el.get_text().split()) if time_el else ""
        
        if title:
            snippet = f"{title} ({time_str})" if time_str else title
            formatted.append({
                "title": f"{title} - {site}",
                "snippet": snippet,
                "url": href
            })
    
    # 2. Regular search snippets — broader results
    for snip in soup.select("div.snippet[data-pos]")[:5]:
        # Brave uses nested structure — get full text and parse
        full_text = " ".join(snip.get_text().split())
        link_el = snip.select_one("a")
        href = link_el["href"] if link_el and link_el.has_attr("href") else "#"
        
        # Split the text: first part is usually site+url, then title, then description
        # Extract the meaningful content (skip short fragments)
        if len(full_text) > 50:
            formatted.append({
                "title": full_text[:120],
                "snippet": full_text,
                "url": href
            })
    
    return formatted


def web_search(query_or_dict: str) -> dict:
    """Multi-Source Signal Acquisition with failover (Phase 47)."""
    query = query_or_dict.get("query") if isinstance(query_or_dict, dict) else query_or_dict
    
    print(f"  🔍 [tool] DDG Search: {query}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        # Primary: DuckDuckGo
        formatted = _scrape_ddg(query, headers)
        
        # Fallback: Brave Search (if DDG blocked/empty)
        if not formatted:
            print(f"  🔄 [tool] DDG blocked/empty. Falling back to Brave Search.")
            formatted = _scrape_brave(query, headers)
            if formatted:
                print(f"  ✅ [tool] Brave fallback: {len(formatted)} results.")
        
        if not formatted:
            return {
                "status": "low_signal", 
                "results": [], 
                "summary": f"No results from any search source for '{query}'."
            }
                
        return {
            "status": "success",
            "results": formatted,
            "summary": f"Retrieved {len(formatted)} snippets for grounding."
        }
    except Exception as e:
        print(f"  🚨 [tool] Search Error: {e}")
        return {
            "status": "error", 
            "reason": str(e), 
            "results": []
        }


TOOLS = {
    "search": web_search,
    "python": run_python,
    "http_fetch": http_fetch,
    "get_time": get_current_time,
    "list_dir": list_dir,
    "read_file": read_file,
    "write_file": write_file,
    "update_ledger": update_ledger
}
