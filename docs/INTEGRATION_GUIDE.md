# Backend Integration Guide

## Quick Start

### 1. Start RAG Service

```bash
cd /home/parthav/work/rag
docker compose up -d rag-service
```

Verify it's running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

---

## Backend Integration Code

### Python/FastAPI Backend

```python
import requests
from typing import Optional

class RAGClient:
    """Client for communicating with RAG service"""
    
    def __init__(self, base_url: str = "http://rag-service:8000"):
        self.base_url = base_url
        self.timeout = 30
    
    def process_s3_document(
        self, 
        tenant_id: str, 
        s3_bucket: str, 
        s3_key: str, 
        filename: str
    ) -> dict:
        """
        Process a document from S3.
        
        Args:
            tenant_id: Unique tenant identifier
            s3_bucket: S3 bucket name
            s3_key: S3 object key (path)
            filename: Original filename
            
        Returns:
            {"status": "success", "chunks_created": 2}
        """
        try:
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def query(self, tenant_id: str, query: str, limit: int = 5) -> dict:
        """
        Query the RAG system.
        
        Args:
            tenant_id: Unique tenant identifier
            query: User's question
            limit: Number of chunks to retrieve
            
        Returns:
            {
                "status": "success",
                "answer": "...",
                "retrieved_chunks": [...]
            }
        """
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={
                    "tenant_id": tenant_id,
                    "query": query,
                    "limit": limit
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def list_documents(self, tenant_id: str) -> dict:
        """List all documents for a tenant"""
        try:
            response = requests.get(
                f"{self.base_url}/files/{tenant_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def delete_document(self, tenant_id: str, filename: str) -> dict:
        """Delete a specific document"""
        try:
            response = requests.delete(
                f"{self.base_url}/documents/{tenant_id}/{filename}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def delete_all_documents(self, tenant_id: str) -> dict:
        """Delete all documents for a tenant"""
        try:
            response = requests.delete(
                f"{self.base_url}/documents/{tenant_id}/all",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def health_check(self) -> bool:
        """Check if RAG service is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# Usage in your FastAPI backend
from fastapi import FastAPI, UploadFile, HTTPException
import boto3

app = FastAPI()
rag = RAGClient()  # Use "http://rag-service:8000" in Docker
s3 = boto3.client('s3')

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile, tenant_id: str):
    """Upload document and process via RAG"""
    
    # 1. Upload to S3
    s3_key = f"{tenant_id}/{file.filename}"
    try:
        s3.upload_fileobj(
            file.file,
            "chatbot-amzs3",
            s3_key
        )
    except Exception as e:
        raise HTTPException(500, f"S3 upload failed: {e}")
    
    # 2. Process via RAG
    result = rag.process_s3_document(
        tenant_id=tenant_id,
        s3_bucket="chatbot-amzs3",
        s3_key=s3_key,
        filename=file.filename
    )
    
    if result.get("status") != "success":
        raise HTTPException(500, f"RAG processing failed: {result.get('message')}")
    
    return {
        "status": "success",
        "filename": file.filename,
        "chunks": result.get("chunks_created")
    }

@app.post("/api/chat")
async def chat(tenant_id: str, query: str):
    """Chat with RAG system"""
    
    result = rag.query(tenant_id, query)
    
    if result.get("status") != "success":
        raise HTTPException(500, f"Query failed: {result.get('message')}")
    
    return {
        "answer": result.get("answer"),
        "sources": [
            chunk.get("source") 
            for chunk in result.get("retrieved_chunks", [])
        ]
    }

@app.get("/api/documents")
async def list_documents(tenant_id: str):
    """List documents for tenant"""
    return rag.list_documents(tenant_id)

@app.delete("/api/documents/{filename}")
async def delete_document(tenant_id: str, filename: str):
    """Delete a document"""
    return rag.delete_document(tenant_id, filename)
```

---

### Node.js/Express Backend

```javascript
const axios = require('axios');
const AWS = require('aws-sdk');

class RAGClient {
    constructor(baseUrl = 'http://rag-service:8000') {
        this.baseUrl = baseUrl;
        this.timeout = 30000;
    }

    async processS3Document(tenantId, s3Bucket, s3Key, filename) {
        try {
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
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async query(tenantId, query, limit = 5) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/query`,
                { tenant_id: tenantId, query, limit },
                { timeout: this.timeout }
            );
            return response.data;
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async listDocuments(tenantId) {
        try {
            const response = await axios.get(
                `${this.baseUrl}/files/${tenantId}`,
                { timeout: this.timeout }
            );
            return response.data;
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async deleteDocument(tenantId, filename) {
        try {
            const response = await axios.delete(
                `${this.baseUrl}/documents/${tenantId}/${filename}`,
                { timeout: this.timeout }
            );
            return response.data;
        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }
}

// Usage
const express = require('express');
const app = express();
const rag = new RAGClient();
const s3 = new AWS.S3();

app.post('/api/chat', async (req, res) => {
    const { tenant_id, query } = req.body;
    const result = await rag.query(tenant_id, query);
    res.json(result);
});
```

---

## Docker Compose with Backend

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - RAG_SERVICE_URL=http://rag-service:8000
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - rag-service
    networks:
      - app-network

  rag-service:
    build: ./knowledge_svc
    # NO port exposure - only accessible via Docker network
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

---

## Testing the Integration

```bash
# 1. Start services
docker compose up -d

# 2. Test RAG health
curl http://localhost:8000/health

# 3. Test from your backend
# Your backend should call http://rag-service:8000 (internal)
# External calls use http://localhost:8000 (for testing only)
```

---

## Production Checklist

- [ ] Remove port exposure for rag-service in docker-compose.yml
- [ ] Add retry logic in RAGClient
- [ ] Add logging for all RAG calls
- [ ] Set up monitoring/alerts
- [ ] Configure resource limits in Docker
- [ ] Add rate limiting if needed
- [ ] Set up backup for Supabase data

---

## Troubleshooting

**RAG service not reachable:**
```bash
# Check if service is running
docker ps

# Check logs
docker logs rag-service

# Test health endpoint
docker exec rag-service curl http://localhost:8000/health
```

**Slow responses:**
- Check embedding model loading (first request is slow)
- Monitor Supabase query performance
- Consider caching frequent queries

**Out of memory:**
```yaml
# Add to docker-compose.yml
services:
  rag-service:
    deploy:
      resources:
        limits:
          memory: 4G
```
