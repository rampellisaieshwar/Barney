import logging
import uuid
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Qdrant client
# Port 6333 is confirmed by research
client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "barney_semantic_memory"

# Initialize embedding model
# all-MiniLM-L6-v2 is confirmed by research
model = SentenceTransformer('all-MiniLM-L6-v2')

def _ensure_collection():
    """Ensure the Qdrant collection exists."""
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    if not exists:
        logger.info(f"Creating Qdrant collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384, # all-MiniLM-L6-v2 dimensions
                distance=models.Distance.COSINE
            ),
        )

def search_memory(user_id: str, query: str) -> str:
    """Search for relevant past conversations."""
    try:
        _ensure_collection()
        query_vector = model.encode(query).tolist()
        
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            ),
            limit=2
        )
        
        if not results:
            return ""
            
        context = "\n--- RELEVANT PAST CONVERSATIONS ---\n"
        for res in results:
            p = res.payload
            context += f"User: {p.get('task')}\nBarney: {p.get('answer')}\n"
        return context + "\n"
    except Exception as e:
        logger.warning(f"Qdrant search failed: {e}")
        return ""

def save_conversation(user_id: str, task: str, answer: str):
    """Save a conversation turn to semantic memory."""
    try:
        _ensure_collection()
        vector = model.encode(task).tolist()
        
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "user_id": user_id,
                        "task": task,
                        "answer": answer,
                        "timestamp": time.time()
                    }
                )
            ]
        )
        logger.info(f"Saved conversation to semantic memory for user {user_id}")
    except Exception as e:
        logger.warning(f"Qdrant save failed: {e}")
