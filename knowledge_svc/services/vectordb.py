import os
import random
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

_client = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client

def ensure_collection(tenant_id: str):
    client = get_qdrant_client()
    collection_name = f"tenant_{tenant_id}_docs"
    
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)
    
    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )
        print(f"Created collection: {collection_name}")
    else:
        print(f"Collection already exists: {collection_name}")

def insert_dummy_vector(tenant_id: str):
    client = get_qdrant_client()
    collection_name = f"tenant_{tenant_id}_docs"
    
    # Ensure collection exists first
    ensure_collection(tenant_id)
    
    dummy_vector = [random.random() for _ in range(768)]
    
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=random.randint(1, 100000),
                vector=dummy_vector,
                payload={"source": "dummy", "text": "This is a dummy vector"}
            )
        ]
    )
    print(f"Inserted dummy vector into {collection_name}")

def search_dummy_vector(tenant_id: str):
    client = get_qdrant_client()
    collection_name = f"tenant_{tenant_id}_docs"
    
    # Ensure collection exists first
    ensure_collection(tenant_id)
    
    dummy_query = [random.random() for _ in range(768)]
    
    results = client.query_points(
        collection_name=collection_name,
        query=dummy_query,
        limit=3
    ).points
    return results

def upsert_chunks(tenant_id: str, chunks: list[str], embeddings: list[list[float]]):
    client = get_qdrant_client()
    collection_name = f"tenant_{tenant_id}_docs"
    
    ensure_collection(tenant_id)
    
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        point_id = str(uuid.uuid4())
        points.append(models.PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "text": chunk,
                "chunk_index": i,
                "source": "upload"
            }
        ))
    
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    print(f"Upserted {len(points)} chunks for {tenant_id}")

def search(tenant_id: str, query_vector: list[float], limit: int = 5) -> list[dict]:
    client = get_qdrant_client()
    collection_name = f"tenant_{tenant_id}_docs"
    
    # Ensure collection exists (though it should for search)
    ensure_collection(tenant_id)
    
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=limit
    ).points
    
    # Format results
    formatted_results = []
    for point in results:
        formatted_results.append({
            "text": point.payload.get("text", ""),
            "score": point.score,
            "source": point.payload.get("source", "")
        })
        
    return formatted_results


