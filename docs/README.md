# Documentation

Complete documentation for the RAG Knowledge Service.

## Quick Links

- **[Integration Guide](INTEGRATION_GUIDE.md)** - How to integrate with your backend (Python & Node.js)
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Next Steps](NEXT_STEPS.md)** - Deployment and production setup
- **[Supabase Setup](SUPABASE_SETUP.md)** - Database initialization
- **[Hallucination Test Results](HALLUCINATION_TEST_RESULTS.md)** - LLM accuracy testing

## Getting Started

1. **Setup**
   - Read [Supabase Setup](SUPABASE_SETUP.md) to initialize your database
   - Configure environment variables (see main README)

2. **Integration**
   - Follow the [Integration Guide](INTEGRATION_GUIDE.md)
   - Use the client code from `../examples/rag_client.py`

3. **Deployment**
   - Check [Next Steps](NEXT_STEPS.md) for Docker deployment
   - Review [API Documentation](API_DOCUMENTATION.md) for endpoint details

## Architecture Overview

```
Backend → RAG Service → S3 (documents)
                    ↓
                Supabase (vectors)
                    ↓
                OpenAI (LLM)
```

## Key Concepts

### Multi-Tenancy
Each tenant has isolated data via `tenant_id`. All API calls require a tenant identifier.

### Document Flow
1. Backend uploads document to S3
2. Backend calls `/process-s3` with S3 path
3. RAG service downloads, chunks, embeds, and stores in Supabase
4. Documents are searchable via `/query`

### Query Flow
1. User asks a question
2. Backend calls `/query` with tenant_id and question
3. RAG service:
   - Embeds the question
   - Searches Supabase for relevant chunks
   - Builds context from top results
   - Calls LLM to generate answer
4. Answer returned to user

## Support

For detailed information, see the individual documentation files in this directory.
