# RAG Service API Documentation

## Base URL
`http://localhost:8080` (or your deployed URL)

## Endpoints

### Health Check
```
GET /health
```
Returns service health status.

---

### Document Upload (Direct)
```
POST /upload-file
Content-Type: multipart/form-data

Parameters:
- tenant_id: string (form field)
- file: file (PDF, DOCX, TXT, MD)

Response:
{
  "status": "success",
  "message": "Successfully processed document.pdf",
  "filename": "document.pdf",
  "chunks_created": 42
}
```

---

### Document Upload (from S3)
```
POST /process-s3
Content-Type: multipart/form-data

Parameters:
- tenant_id: string
- s3_bucket: string
- s3_key: string (e.g., "tenant_123/document.pdf")
- filename: string

Response:
{
  "status": "success",
  "message": "Successfully processed document.pdf",
  "chunks_created": 42,
  "s3_path": "s3://bucket/tenant_123/document.pdf"
}
```

**Usage from Backend:**
```python
import requests

response = requests.post(
    "http://rag-service:8080/process-s3",
    data={
        "tenant_id": "tenant_123",
        "s3_bucket": "my-documents",
        "s3_key": "tenant_123/report.pdf",
        "filename": "report.pdf"
    }
)
```

---

### Query Knowledge Base
```
POST /query
Content-Type: application/json

Body:
{
  "tenant_id": "tenant_123",
  "query": "What is plutonium used for?"
}

Response:
{
  "status": "success",
  "answer": "Plutonium is used...",
  "retrieved_chunks": [
    {
      "text": "...",
      "score": 0.85,
      "source": "document.pdf"
    }
  ]
}
```

---

### List Documents
```
GET /files/{tenant_id}

Response:
{
  "status": "success",
  "tenant_id": "tenant_123",
  "files": [
    {
      "filename": "document.pdf",
      "file_type": ".pdf",
      "upload_date": "2026-01-15T...",
      "chunk_count": 42
    }
  ]
}
```

---

### Delete Document
```
DELETE /documents/{tenant_id}/{filename}

Response:
{
  "status": "success",
  "message": "Deleted document.pdf",
  "chunks_deleted": 42
}
```

---

### Delete All Documents (Clear Knowledge Base)
```
DELETE /documents/{tenant_id}/all

Response:
{
  "status": "success",
  "message": "Deleted all documents for tenant tenant_123",
  "chunks_deleted": 150
}
```

---

## Environment Variables

Required:
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
OPENAI_API_KEY=sk-proj-...
```

Optional (for S3):
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-documents
```

---

## Integration Example (Backend → RAG)

### Python Backend Example
```python
import requests

class RAGClient:
    def __init__(self, base_url="http://rag-service:8080"):
        self.base_url = base_url
    
    def process_s3_document(self, tenant_id, s3_bucket, s3_key, filename):
        """Process document from S3"""
        response = requests.post(
            f"{self.base_url}/process-s3",
            data={
                "tenant_id": tenant_id,
                "s3_bucket": s3_bucket,
                "s3_key": s3_key,
                "filename": filename
            }
        )
        return response.json()
    
    def query(self, tenant_id, query):
        """Query RAG system"""
        response = requests.post(
            f"{self.base_url}/query",
            json={"tenant_id": tenant_id, "query": query}
        )
        return response.json()
    
    def delete_document(self, tenant_id, filename):
        """Delete specific document"""
        response = requests.delete(
            f"{self.base_url}/documents/{tenant_id}/{filename}"
        )
        return response.json()
    
    def list_documents(self, tenant_id):
        """List all documents"""
        response = requests.get(
            f"{self.base_url}/files/{tenant_id}"
        )
        return response.json()
```

### Usage
```python
rag = RAGClient()

# Process document from S3
result = rag.process_s3_document(
    tenant_id="tenant_123",
    s3_bucket="my-docs",
    s3_key="tenant_123/report.pdf",
    filename="report.pdf"
)

# Query
answer = rag.query("tenant_123", "What is in the report?")
print(answer["answer"])

# List documents
docs = rag.list_documents("tenant_123")

# Delete document
rag.delete_document("tenant_123", "report.pdf")
```

---

## Error Handling

All endpoints return consistent error format:
```json
{
  "status": "error",
  "message": "Error description"
}
```

Common errors:
- `400`: Invalid request (missing parameters)
- `404`: Document not found
- `500`: Server error (S3 failure, DB error, etc.)
