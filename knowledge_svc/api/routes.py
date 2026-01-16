from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from datetime import datetime
from .models import (
    UploadRequest, UploadResponse, QueryRequest, QueryResponse,
    FileUploadResponse, FileListResponse
)
from ..services import vectordb, embedder, chunker, context_builder, llm, file_parser

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

@router.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(tenant_id: str = Form(...), file: UploadFile = File(...)):
    """
    Upload a single file (PDF, DOCX, TXT, or Markdown).
    """
    print(f"Received file upload for tenant {tenant_id}: {file.filename}")
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Parse file based on extension
    try:
        text = file_parser.parse_file(file.filename, file_bytes)
    except ValueError as e:
        return FileUploadResponse(
            status="error",
            message=str(e),
            filename=file.filename,
            chunks_created=0
        )
    
    # Process the text
    chunks = chunker.chunk_text(text)
    print(f"Generated {len(chunks)} chunks from {file.filename}")
    
    # Embed chunks
    embeddings = []
    for chunk in chunks:
        vector = embedder.embed_document(chunk)
        embeddings.append(vector)
    
    # Store with file metadata
    upload_time = datetime.utcnow().isoformat()
    vectordb.upsert_chunks(
        tenant_id=tenant_id,
        chunks=chunks,
        embeddings=embeddings,
        source_file=file.filename,
        file_type=file_parser.get_file_extension(file.filename),
        upload_timestamp=upload_time
    )
    
    return FileUploadResponse(
        status="success",
        message=f"Successfully processed {file.filename}",
        filename=file.filename,
        chunks_created=len(chunks)
    )

@router.post("/upload-files")
async def upload_multiple_files(tenant_id: str = Form(...), files: List[UploadFile] = File(...)):
    """
    Upload multiple files at once.
    """
    results = []
    
    for file in files:
        try:
            file_bytes = await file.read()
            text = file_parser.parse_file(file.filename, file_bytes)
            chunks = chunker.chunk_text(text)
            
            embeddings = [embedder.embed_document(chunk) for chunk in chunks]
            
            upload_time = datetime.utcnow().isoformat()
            vectordb.upsert_chunks(
                tenant_id=tenant_id,
                chunks=chunks,
                embeddings=embeddings,
                source_file=file.filename,
                file_type=file_parser.get_file_extension(file.filename),
                upload_timestamp=upload_time
            )
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "chunks_created": len(chunks)
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {"status": "completed", "results": results}

@router.get("/files/{tenant_id}", response_model=FileListResponse)
async def list_files(tenant_id: str):
    """
    List all uploaded files for a tenant.
    """
    files = vectordb.list_files(tenant_id)
    return FileListResponse(
        status="success",
        tenant_id=tenant_id,
        files=files
    )

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

@router.post("/process-s3")
async def process_s3_document(
    tenant_id: str = Form(...),
    s3_bucket: str = Form(...),
    s3_key: str = Form(...),
    filename: str = Form(...)
):
    """
    Process a document from S3.
    
    Args:
        tenant_id: Tenant ID
        s3_bucket: S3 bucket name
        s3_key: S3 object key (path)
        filename: Original filename
    
    Returns:
        Processing status and metadata
    """
    print(f"Processing S3 document for tenant {tenant_id}: s3://{s3_bucket}/{s3_key}")
    
    try:
        # Import S3 client
        from ..services import s3_client
        
        # Download from S3
        file_bytes = s3_client.download_from_s3(s3_bucket, s3_key)
        
        if not file_bytes:
            return {
                "status": "error",
                "message": "Failed to download file from S3"
            }
        
        # Parse file
        text = file_parser.parse_file(filename, file_bytes)
        
        # Process: chunk → embed → store
        chunks = chunker.chunk_text(text)
        embeddings = [embedder.embed_document(chunk) for chunk in chunks]
        
        upload_time = datetime.utcnow().isoformat()
        vectordb.upsert_chunks(
            tenant_id=tenant_id,
            chunks=chunks,
            embeddings=embeddings,
            source_file=filename,
            file_type=file_parser.get_file_extension(filename),
            upload_timestamp=upload_time
        )
        
        return {
            "status": "success",
            "message": f"Successfully processed {filename}",
            "chunks_created": len(chunks),
            "s3_path": f"s3://{s3_bucket}/{s3_key}"
        }
    
    except Exception as e:
        print(f"Error processing S3 document: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.delete("/documents/{tenant_id}/{filename}")
async def delete_document(tenant_id: str, filename: str):
    """
    Delete a specific document and all its chunks.
    
    Args:
        tenant_id: Tenant ID
        filename: Filename to delete
    
    Returns:
        Deletion status
    """
    print(f"Deleting document {filename} for tenant {tenant_id}")
    
    try:
        deleted_count = vectordb.delete_document(tenant_id, filename)
        
        return {
            "status": "success",
            "message": f"Deleted {filename}",
            "chunks_deleted": deleted_count
        }
    
    except Exception as e:
        print(f"Error deleting document: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.delete("/documents/{tenant_id}/all")
async def delete_all_documents(tenant_id: str):
    """
    Delete ALL documents for a tenant (clear knowledge base).
    
    Args:
        tenant_id: Tenant ID
    
    Returns:
        Deletion status
    """
    print(f"Deleting ALL documents for tenant {tenant_id}")
    
    try:
        deleted_count = vectordb.delete_all_documents(tenant_id)
        
        return {
            "status": "success",
            "message": f"Deleted all documents for tenant {tenant_id}",
            "chunks_deleted": deleted_count
        }
    
    except Exception as e:
        print(f"Error deleting all documents: {e}")
        return {
            "status": "error",
            "message": str(e)
        }



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




