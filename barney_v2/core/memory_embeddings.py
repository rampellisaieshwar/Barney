import numpy as np
import time

_model = None

def get_model():
    """Lazy Singleton Model Loading (Fix #2)."""
    global _model
    if _model is None:
        print("  🧩 [embeddings] Loading sentence-transformer (all-MiniLM-L6-v2)...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def normalize(v):
    """L2 Normalization for accurate dot-product similarity (Fix #3)."""
    norm = np.linalg.norm(v)
    if norm == 0: return v
    return v / norm

def embed_text(text: str):
    """Generates a rounded 384-d vector for a given string (Fix #1)."""
    try:
        model = get_model()
        # Encode returns a numpy array
        raw_vec = model.encode(text)
        # Round to 6 decimal places to reduce JSON storage bloat
        rounded_vec = [round(float(x), 6) for x in raw_vec]
        return rounded_vec
    except Exception as e:
        print(f"  🚨 [embeddings] Embedding failure: {e}")
        return None

def cosine_similarity(v1, v2):
    """Calculates cosine similarity between two vectors."""
    if v1 is None or v2 is None: return 0.0
    vec1 = normalize(np.array(v1))
    vec2 = normalize(np.array(v2))
    return float(np.dot(vec1, vec2))

def recency_score(timestamp_ns):
    """Exponential Decay for temporal relevance (Fix #4).
    Normalized to 1.0 for now, decaying over a 1-week half-life.
    """
    now_ns = time.time_ns()
    # Convert ns to seconds
    age_sec = (now_ns - timestamp_ns) / 1e9
    # 1 week = 604800 seconds
    return float(np.exp(-age_sec / 604800))
