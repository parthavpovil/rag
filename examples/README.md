# Backend Integration Examples

This directory contains example code for integrating the RAG service with your backend.

## Files

### `rag_client.py`
Drop-in Python client for calling the RAG service from your backend.

**Usage:**
```python
from examples.rag_client import RAGClient

# Initialize client
rag = RAGClient("http://rag-service:8000")  # Docker
# or
rag = RAGClient("http://localhost:8000")  # Local testing

# Process document from S3
result = rag.process_s3_document(
    tenant_id="tenant_123",
    s3_bucket="my-bucket",
    s3_key="tenant_123/document.pdf",
    filename="document.pdf"
)

# Query
answer = rag.query("tenant_123", "What is in the document?")
print(answer["answer"])

# List documents
docs = rag.list_documents("tenant_123")

# Delete document
rag.delete_document("tenant_123", "document.pdf")
```

## FastAPI Integration Example

```python
from fastapi import FastAPI, UploadFile, HTTPException
from examples.rag_client import RAGClient
import boto3

app = FastAPI()
rag = RAGClient("http://rag-service:8000")
s3 = boto3.client('s3')

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile, tenant_id: str):
    """Upload document and process via RAG"""
    
    # 1. Upload to S3
    s3_key = f"{tenant_id}/{file.filename}"
    s3.upload_fileobj(file.file, "my-bucket", s3_key)
    
    # 2. Process via RAG
    result = rag.process_s3_document(
        tenant_id, "my-bucket", s3_key, file.filename
    )
    
    if result.get("status") != "success":
        raise HTTPException(500, "Processing failed")
    
    return {"status": "success", "chunks": result.get("chunks_created")}

@app.post("/api/chat")
async def chat(tenant_id: str, query: str):
    """Chat with RAG system"""
    result = rag.query(tenant_id, query)
    return {"answer": result.get("answer")}
```

## Node.js Integration Example

```javascript
const axios = require('axios');

class RAGClient {
    constructor(baseUrl = 'http://rag-service:8000') {
        this.baseUrl = baseUrl;
    }

    async query(tenantId, query) {
        const response = await axios.post(`${this.baseUrl}/query`, {
            tenant_id: tenantId,
            query: query
        });
        return response.data;
    }
}

// Usage
const rag = new RAGClient();
const result = await rag.query('tenant_123', 'What is in the document?');
console.log(result.answer);
```

## Error Handling

Always check the `status` field in responses:

```python
result = rag.query(tenant_id, query)

if result.get("status") == "error":
    # Handle error
    print(f"Error: {result.get('message')}")
else:
    # Success
    print(result.get("answer"))
```

## See Also

- [Integration Guide](../docs/INTEGRATION_GUIDE.md) - Complete integration documentation
- [API Documentation](../docs/API_DOCUMENTATION.md) - Full API reference
