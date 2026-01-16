import os
import uuid
from datetime import datetime
from supabase import create_client, Client
from typing import List, Dict

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_client = None

def get_supabase_client() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

def ensure_table():
    """
    Ensure the knowledge_vectors table exists.
    Note: Table creation should be done via init_supabase.sql
    This function just verifies connectivity.
    """
    client = get_supabase_client()
    try:
        # Simple query to verify table exists
        client.table("knowledge_vectors").select("id").limit(1).execute()
        print("✓ knowledge_vectors table is accessible")
    except Exception as e:
        print(f"⚠ Warning: Could not access knowledge_vectors table: {e}")
        print("Please run init_supabase.sql in your Supabase SQL editor")

def ensure_collection(tenant_id: str):
    """
    Legacy function for compatibility.
    In Supabase, we use a single table with tenant_id column.
    """
    ensure_table()

def insert_dummy_vector(tenant_id: str):
    """Insert a dummy vector for testing purposes."""
    client = get_supabase_client()
    
    import random
    dummy_vector = [random.random() for _ in range(768)]
    
    data = {
        "tenant_id": tenant_id,
        "vector": dummy_vector,
        "text": "This is a dummy vector",
        "chunk_index": 0,
        "source_file": "dummy",
        "file_type": ".txt",
        "upload_timestamp": datetime.now().isoformat()
    }
    
    result = client.table("knowledge_vectors").insert(data).execute()
    print(f"Inserted dummy vector for tenant {tenant_id}")
    return result

def search_dummy_vector(tenant_id: str):
    """Search using a dummy query vector."""
    client = get_supabase_client()
    
    import random
    dummy_query = [random.random() for _ in range(768)]
    
    # Use RPC function for vector similarity search
    # Note: This requires a custom SQL function in Supabase
    results = client.rpc(
        "match_knowledge_vectors",
        {
            "query_embedding": dummy_query,
            "match_tenant_id": tenant_id,
            "match_count": 3
        }
    ).execute()
    
    return results.data if results.data else []

def upsert_chunks(
    tenant_id: str,
    chunks: List[str],
    embeddings: List[List[float]],
    source_file: str = "upload",
    file_type: str = ".txt",
    upload_timestamp: str = None
):
    """
    Insert document chunks with their embeddings into Supabase.
    """
    client = get_supabase_client()
    
    if not upload_timestamp:
        upload_timestamp = datetime.now().isoformat()
    
    # Prepare batch insert data
    data = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        data.append({
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "vector": vector,
            "text": chunk,
            "chunk_index": i,
            "source_file": source_file,
            "file_type": file_type,
            "upload_timestamp": upload_timestamp
        })
    
    # Insert all chunks in one batch
    result = client.table("knowledge_vectors").insert(data).execute()
    print(f"✓ Upserted {len(data)} chunks for tenant {tenant_id}")
    return result

def search(tenant_id: str, query_vector: List[float], limit: int = 5) -> List[Dict]:
    """
    Search for similar vectors using pgvector cosine similarity.
    """
    client = get_supabase_client()
    
    try:
        # Use RPC function for vector similarity search
        results = client.rpc(
            "match_knowledge_vectors",
            {
                "query_embedding": query_vector,
                "match_tenant_id": tenant_id,
                "match_count": limit
            }
        ).execute()
        
        if not results.data:
            return []
        
        # Format results to match expected output
        formatted_results = []
        for row in results.data:
            formatted_results.append({
                "text": row.get("text", ""),
                "score": row.get("similarity", 0.0),
                "source": row.get("source_file", "")
            })
        
        return formatted_results
    
    except Exception as e:
        print(f"Error during search: {e}")
        print("Make sure you've created the match_knowledge_vectors RPC function in Supabase")
        return []

def list_files(tenant_id: str) -> List[Dict]:
    """
    List all uploaded files for a tenant.
    Returns file metadata grouped by filename.
    """
    client = get_supabase_client()
    
    try:
        # Query all chunks for this tenant
        result = client.table("knowledge_vectors")\
            .select("source_file, file_type, upload_timestamp")\
            .eq("tenant_id", tenant_id)\
            .execute()
        
        if not result.data:
            return []
        
        # Group by source_file
        files_dict = {}
        for row in result.data:
            filename = row.get("source_file", "unknown")
            
            if filename not in files_dict:
                files_dict[filename] = {
                    "filename": filename,
                    "file_type": row.get("file_type", ""),
                    "upload_date": row.get("upload_timestamp", ""),
                    "chunk_count": 0
                }
            
            files_dict[filename]["chunk_count"] += 1
        
        return list(files_dict.values())
    
    except Exception as e:
        print(f"Error listing files for {tenant_id}: {e}")
        return []

def delete_document(tenant_id: str, source_file: str) -> int:
    """
    Delete all chunks for a specific document.
    
    Args:
        tenant_id: Tenant ID
        source_file: Source filename to delete
    
    Returns:
        Number of chunks deleted
    """
    client = get_supabase_client()
    
    try:
        # Delete all chunks for this document
        result = client.table("knowledge_vectors")\
            .delete()\
            .eq("tenant_id", tenant_id)\
            .eq("source_file", source_file)\
            .execute()
        
        # Count deleted rows (Supabase returns deleted rows)
        deleted_count = len(result.data) if result.data else 0
        print(f"✓ Deleted {deleted_count} chunks for {source_file} (tenant: {tenant_id})")
        return deleted_count
    
    except Exception as e:
        print(f"Error deleting document {source_file} for {tenant_id}: {e}")
        raise

def delete_all_documents(tenant_id: str) -> int:
    """
    Delete all documents/chunks for a tenant.
    
    Args:
        tenant_id: Tenant ID
    
    Returns:
        Number of chunks deleted
    """
    client = get_supabase_client()
    
    try:
        # Delete all chunks for this tenant
        result = client.table("knowledge_vectors")\
            .delete()\
            .eq("tenant_id", tenant_id)\
            .execute()
        
        deleted_count = len(result.data) if result.data else 0
        print(f"✓ Deleted {deleted_count} total chunks for tenant {tenant_id}")
        return deleted_count
    
    except Exception as e:
        print(f"Error deleting all documents for {tenant_id}: {e}")
        raise
