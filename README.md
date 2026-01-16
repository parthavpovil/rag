# RAG Knowledge Service

A production-ready Retrieval-Augmented Generation (RAG) system with S3 integration, Supabase vector storage, and multi-tenant support.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS S3 bucket
- Supabase account
- OpenAI API key

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# OpenAI
OPENAI_API_KEY=sk-proj-xxx

# AWS S3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-southeast-2
S3_BUCKET_NAME=your-bucket
```

### 2. Initialize Supabase

Run the SQL script in your Supabase SQL editor:
```bash
cat knowledge_svc/init_supabase.sql
```

### 3. Start the Service

```bash
docker compose up -d
```

Verify it's running:
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

## 📚 Documentation

- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - How to integrate with your backend
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Next Steps](docs/NEXT_STEPS.md)** - Deployment guide
- **[Supabase Setup](docs/SUPABASE_SETUP.md)** - Database initialization

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Client    │────────▶│  Your Backend    │────────▶│     S3      │
└─────────────┘         └──────────────────┘         └─────────────┘
                                │                            ▲
                                │ HTTP                       │
                                ▼                            │
                        ┌──────────────────┐                │
                        │  RAG Service     │────────────────┘
                        │  (port 8000)     │
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │    Supabase      │
                        │  (Vector Store)  │
                        └──────────────────┘
```

## 🔌 Backend Integration

### Python Example

```python
from examples.rag_client import RAGClient

rag = RAGClient("http://rag-service:8000")

# Upload and process document
result = rag.process_s3_document(
    tenant_id="tenant_123",
    s3_bucket="my-bucket",
    s3_key="tenant_123/document.pdf",
    filename="document.pdf"
)

# Query
answer = rag.query("tenant_123", "What is in the document?")
print(answer["answer"])
```

See [examples/rag_client.py](examples/rag_client.py) for the complete client.

## 📋 API Endpoints

### Document Processing
- `POST /process-s3` - Process document from S3
- `POST /upload-file` - Direct file upload
- `GET /files/{tenant_id}` - List documents
- `DELETE /documents/{tenant_id}/{filename}` - Delete document
- `DELETE /documents/{tenant_id}/all` - Clear knowledge base

### Querying
- `POST /query` - Query the RAG system
- `GET /health` - Health check

See [API Documentation](docs/API_DOCUMENTATION.md) for details.

## 🧪 Testing

```bash
# Run tests
cd tests
python test_e2e_rag.py
python test_s3_upload_and_query.py
```

## 🛠️ Development

### Project Structure

```
rag/
├── knowledge_svc/          # Main service code
│   ├── api/                # API routes
│   ├── services/           # Business logic
│   │   ├── chunker.py      # Text chunking
│   │   ├── embedder.py     # Embedding generation
│   │   ├── vectordb.py     # Supabase integration
│   │   ├── s3_client.py    # S3 operations
│   │   ├── llm.py          # LLM integration
│   │   └── file_parser.py  # Document parsing
│   ├── main.py             # FastAPI app
│   ├── Dockerfile          # Container definition
│   └── requirements.txt    # Python dependencies
├── docs/                   # Documentation
├── examples/               # Integration examples
├── tests/                  # Test files
├── docker-compose.yml      # Docker configuration
└── .env                    # Environment variables
```

### Local Development

```bash
# Install dependencies
cd knowledge_svc
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --port 8000
```

## 🔐 Security

- RAG service should NOT be exposed to the internet in production
- Backend acts as gateway and validates all requests
- Tenant isolation enforced via `tenant_id`
- Use service role key for Supabase (bypasses RLS)

## 📊 Features

✅ Multi-tenant support  
✅ S3 document storage  
✅ Supabase vector database  
✅ Multiple file formats (PDF, DOCX, TXT, MD)  
✅ Semantic search with embeddings  
✅ LLM answer generation  
✅ Document management (list, delete)  
✅ Docker deployment  
✅ Health checks  

## 🚧 Roadmap

- [ ] Streaming responses
- [ ] Query caching
- [ ] Rate limiting
- [ ] Usage analytics
- [ ] Async document processing
- [ ] Multi-language support

## 📝 License

MIT

## 🤝 Support

For issues or questions, see the [documentation](docs/) or create an issue.

---

**Built with:** FastAPI, Supabase, OpenAI, Sentence Transformers, AWS S3
