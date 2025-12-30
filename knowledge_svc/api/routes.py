from fastapi import APIRouter
from .models import UploadRequest, UploadResponse, QueryRequest, QueryResponse
from ..services import vectordb, embedder, chunker, context_builder, llm

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/upload", response_model=UploadResponse)
async def upload_text(request: UploadRequest):
    print(f"Received upload for tenant {request.tenant_id}: {len(request.raw_text)} chars")
    
    # 1. Chunking
    chunks = chunker.chunk_text(request.raw_text)
    print(f"Generated {len(chunks)} chunks")
    
    # 2. Embedding
    embeddings = []
    for chunk in chunks:
        vector = embedder.embed_document(chunk)
        embeddings.append(vector)
    print(f"Generated {len(embeddings)} embeddings")
    
    # 3. Storage
    vectordb.upsert_chunks(request.tenant_id, chunks, embeddings)
    
    return UploadResponse(status="processed", message=f"Successfully processed {len(chunks)} chunks")


@router.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    print(f"Received query for tenant {request.tenant_id}: {request.query}")
    
    # 1. Embed query
    query_vector = embedder.embed_query(request.query)
    
    # 2. Search Vector DB
    results = vectordb.search(request.tenant_id, query_vector)
    
    # 3. Build Context
    context = context_builder.build_context(results)
    
    # 4. Generate Answer
    answer = llm.generate_answer(request.query, context)
    
    return QueryResponse(
        status="success", 
        answer=answer,
        retrieved_chunks=results
    )



# Debug endpoints
@router.post("/debug/init-collection")
async def debug_init_collection(tenant_id: str):
    vectordb.ensure_collection(tenant_id)
    return {"status": "ok", "message": f"Collection ensured for {tenant_id}"}

@router.post("/debug/insert-dummy")
async def debug_insert_dummy(tenant_id: str):
    vectordb.insert_dummy_vector(tenant_id)
    return {"status": "ok", "message": f"Dummy vector inserted for {tenant_id}"}

@router.post("/debug/search-dummy")
async def debug_search_dummy(tenant_id: str):
    results = vectordb.search_dummy_vector(tenant_id)
    return {"status": "ok", "results": results}

@router.post("/debug/embed-doc")
async def debug_embed_doc(text: str):
    vector = embedder.embed_document(text)
    return {"status": "ok", "vector_length": len(vector), "vector_preview": vector[:5]}

@router.post("/debug/embed-query")
async def debug_embed_query(text: str):
    vector = embedder.embed_query(text)
    return {"status": "ok", "vector_length": len(vector), "vector_preview": vector[:5]}

@router.post("/debug/chunk")
async def debug_chunk(text: str, chunk_size: int = 1000, overlap: int = 200):
    chunks = chunker.chunk_text(text, chunk_size, overlap)
    return {"status": "ok", "num_chunks": len(chunks), "chunks": chunks}

@router.post("/debug/build-context")
async def debug_build_context(chunks: list[dict]):
    context = context_builder.build_context(chunks)
    return {"status": "ok", "context": context}




