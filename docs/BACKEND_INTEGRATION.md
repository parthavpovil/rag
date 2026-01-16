# Backend Integration Guide - Step by Step

This guide walks you through integrating the RAG service with your existing backend, step by step.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step 1: Deploy RAG Service](#step-1-deploy-rag-service)
4. [Step 2: Add Client Code](#step-2-add-client-code)
5. [Step 3: Implement Upload Flow](#step-3-implement-upload-flow)
6. [Step 4: Implement Query Flow](#step-4-implement-query-flow)
7. [Step 5: Add Document Management](#step-5-add-document-management)
8. [Testing](#testing)
9. [Production Checklist](#production-checklist)

---

## Prerequisites

✅ Docker and Docker Compose installed  
✅ AWS S3 bucket configured  
✅ Supabase account with database initialized  
✅ OpenAI API key  
✅ Your backend service (Python/FastAPI, Node.js/Express, etc.)

---

## Architecture Overview

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────────────────────────────┐
│         Your Backend Service         │
│  ┌────────────────────────────────┐  │
│  │  1. Validate tenant/auth       │  │
│  │  2. Upload file to S3          │  │
│  │  3. Call RAG service           │  │
│  │  4. Return response            │  │
│  └────────────────────────────────┘  │
└──────────────┬───────────────────────┘
               │ HTTP (Docker network)
               ▼
       ┌───────────────┐
       │  RAG Service  │
       │  (port 8000)  │
       └───┬───────┬───┘
           │       │
           │       └──────────┐
           ▼                  ▼
    ┌──────────┐      ┌──────────────┐
    │    S3    │      │   Supabase   │
    │ (Docs)   │      │  (Vectors)   │
    └──────────┘      └──────────────┘
```

**Key Points:**
- Your backend is the **only** entry point for clients
- RAG service is **internal** (not exposed to internet)
- Communication via Docker network (fast & secure)

---

## Step 1: Deploy RAG Service

### 1.1 Configure Environment

```bash
cd /path/to/rag
cp .env.example .env
```

Edit `.env`:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
OPENAI_API_KEY=sk-proj-xxx
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-southeast-2
S3_BUCKET_NAME=your-bucket
```

### 1.2 Initialize Supabase

Run the SQL script in Supabase SQL Editor:
```bash
cat knowledge_svc/init_supabase.sql
```

Copy and paste the entire content into Supabase SQL Editor and run.

### 1.3 Start RAG Service

```bash
docker compose up -d rag-service
```

Verify:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

---

## Step 2: Add Client Code

### Option A: Python Backend

Copy the client into your backend:
```bash
cp examples/rag_client.py /path/to/your/backend/services/rag_client.py
```

Or install as a package:
```python
# your_backend/services/rag_client.py
import requests
from typing import Dict

class RAGClient:
    def __init__(self, base_url: str = "http://rag-service:8000"):
        self.base_url = base_url
        self.timeout = 30
    
    def process_s3_document(self, tenant_id: str, s3_bucket: str, 
                           s3_key: str, filename: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/process-s3",
            data={
                "tenant_id": tenant_id,
                "s3_bucket": s3_bucket,
                "s3_key": s3_key,
                "filename": filename
            },
            timeout=self.timeout
        )
        return response.json()
    
    def query(self, tenant_id: str, query: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/query",
            json={"tenant_id": tenant_id, "query": query},
            timeout=self.timeout
        )
        return response.json()
```

### Option B: Node.js Backend

```javascript
// your_backend/services/ragClient.js
const axios = require('axios');

class RAGClient {
    constructor(baseUrl = 'http://rag-service:8000') {
        this.baseUrl = baseUrl;
        this.timeout = 30000;
    }

    async processS3Document(tenantId, s3Bucket, s3Key, filename) {
        const response = await axios.post(
            `${this.baseUrl}/process-s3`,
            new URLSearchParams({
                tenant_id: tenantId,
                s3_bucket: s3Bucket,
                s3_key: s3Key,
                filename: filename
            }),
            { timeout: this.timeout }
        );
        return response.data;
    }

    async query(tenantId, query) {
        const response = await axios.post(
            `${this.baseUrl}/query`,
            { tenant_id: tenantId, query },
            { timeout: this.timeout }
        );
        return response.data;
    }
}

module.exports = RAGClient;
```

---

## Step 3: Implement Upload Flow

### Python/FastAPI Example

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from services.rag_client import RAGClient
import boto3
import os

app = FastAPI()
rag = RAGClient()
s3 = boto3.client('s3')

def get_current_tenant(token: str) -> str:
    """Your existing auth logic"""
    # Validate token and return tenant_id
    return "tenant_123"  # Replace with actual logic

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Upload document and process via RAG.
    
    Flow:
    1. Validate tenant (done by dependency)
    2. Upload to S3
    3. Trigger RAG processing
    4. Return status
    """
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, f"File type {file_ext} not supported")
    
    # Upload to S3
    s3_key = f"{tenant_id}/{file.filename}"
    try:
        s3.upload_fileobj(
            file.file,
            os.getenv("S3_BUCKET_NAME"),
            s3_key
        )
    except Exception as e:
        raise HTTPException(500, f"S3 upload failed: {str(e)}")
    
    # Process via RAG
    result = rag.process_s3_document(
        tenant_id=tenant_id,
        s3_bucket=os.getenv("S3_BUCKET_NAME"),
        s3_key=s3_key,
        filename=file.filename
    )
    
    if result.get("status") != "success":
        raise HTTPException(500, f"RAG processing failed: {result.get('message')}")
    
    return {
        "status": "success",
        "document_id": file.filename,
        "chunks_created": result.get("chunks_created"),
        "message": f"Document {file.filename} processed successfully"
    }
```

### Node.js/Express Example

```javascript
const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const RAGClient = require('./services/ragClient');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });
const s3 = new AWS.S3();
const rag = new RAGClient();

app.post('/api/v1/documents/upload', 
    authenticateToken,  // Your auth middleware
    upload.single('file'),
    async (req, res) => {
        const tenantId = req.user.tenantId;  // From your auth
        const file = req.file;
        
        // Upload to S3
        const s3Key = `${tenantId}/${file.originalname}`;
        await s3.putObject({
            Bucket: process.env.S3_BUCKET_NAME,
            Key: s3Key,
            Body: file.buffer
        }).promise();
        
        // Process via RAG
        const result = await rag.processS3Document(
            tenantId,
            process.env.S3_BUCKET_NAME,
            s3Key,
            file.originalname
        );
        
        res.json({
            status: 'success',
            document_id: file.originalname,
            chunks_created: result.chunks_created
        });
    }
);
```

---

## Step 4: Implement Query Flow

### Python/FastAPI Example

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Chat with RAG system.
    
    Flow:
    1. Validate tenant
    2. Call RAG service
    3. Return answer with sources
    """
    
    result = rag.query(tenant_id, request.query)
    
    if result.get("status") != "success":
        raise HTTPException(500, f"Query failed: {result.get('message')}")
    
    # Extract sources from retrieved chunks
    sources = [
        chunk.get("source", "unknown")
        for chunk in result.get("retrieved_chunks", [])
    ]
    
    return ChatResponse(
        answer=result.get("answer"),
        sources=list(set(sources))  # Unique sources
    )
```

### Node.js/Express Example

```javascript
app.post('/api/v1/chat', authenticateToken, async (req, res) => {
    const tenantId = req.user.tenantId;
    const { query } = req.body;
    
    const result = await rag.query(tenantId, query);
    
    if (result.status !== 'success') {
        return res.status(500).json({ error: result.message });
    }
    
    // Extract unique sources
    const sources = [...new Set(
        result.retrieved_chunks.map(chunk => chunk.source)
    )];
    
    res.json({
        answer: result.answer,
        sources: sources
    });
});
```

---

## Step 5: Add Document Management

### List Documents

```python
@app.get("/api/v1/documents")
async def list_documents(tenant_id: str = Depends(get_current_tenant)):
    """List all documents for tenant"""
    result = rag.list_documents(tenant_id)
    return result.get("files", [])
```

### Delete Document

```python
@app.delete("/api/v1/documents/{filename}")
async def delete_document(
    filename: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Delete a specific document"""
    result = rag.delete_document(tenant_id, filename)
    
    if result.get("status") != "success":
        raise HTTPException(500, "Delete failed")
    
    return {"status": "success", "message": f"Deleted {filename}"}
```

### Clear Knowledge Base

```python
@app.delete("/api/v1/documents")
async def clear_knowledge_base(tenant_id: str = Depends(get_current_tenant)):
    """Delete all documents for tenant"""
    result = rag.delete_all_documents(tenant_id)
    return {
        "status": "success",
        "chunks_deleted": result.get("chunks_deleted", 0)
    }
```

---

## Testing

### 1. Test RAG Service Directly

```bash
# Health check
curl http://localhost:8000/health

# Upload test (after uploading to S3)
curl -X POST http://localhost:8000/process-s3 \
  -F "tenant_id=test_tenant" \
  -F "s3_bucket=your-bucket" \
  -F "s3_key=test_tenant/test.txt" \
  -F "filename=test.txt"

# Query test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"test_tenant","query":"test question"}'
```

### 2. Test Your Backend

```bash
# Upload
curl -X POST http://localhost:3000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# Chat
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is in the document?"}'
```

---

## Production Checklist

### Security
- [ ] Remove port exposure for RAG service in `docker-compose.yml`
- [ ] Use environment variables for all secrets
- [ ] Implement rate limiting on your backend
- [ ] Add request validation
- [ ] Enable CORS properly

### Monitoring
- [ ] Add logging for all RAG calls
- [ ] Set up health check monitoring
- [ ] Track usage per tenant
- [ ] Monitor response times
- [ ] Set up alerts for failures

### Performance
- [ ] Configure resource limits in Docker
- [ ] Add caching for frequent queries
- [ ] Consider async processing for large uploads
- [ ] Monitor Supabase query performance

### Docker Compose for Production

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - RAG_SERVICE_URL=http://rag-service:8000
    depends_on:
      - rag-service
    networks:
      - app-network

  rag-service:
    build: ./rag/knowledge_svc
    # NO port exposure - internal only
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

---

## Troubleshooting

### RAG service not reachable
```bash
docker ps  # Check if running
docker logs rag-service  # Check logs
docker exec rag-service curl http://localhost:8000/health
```

### Slow responses
- First request is slow (model loading) - normal
- Check Supabase query performance
- Monitor OpenAI API latency

### Out of memory
Add resource limits in docker-compose.yml (see above)

---

## Next Steps

1. **Deploy to staging** - Test with real users
2. **Monitor performance** - Track metrics
3. **Optimize** - Add caching, async processing
4. **Scale** - Add more RAG service instances if needed

For more details, see:
- [API Documentation](API_DOCUMENTATION.md)
- [Next Steps Guide](NEXT_STEPS.md)
