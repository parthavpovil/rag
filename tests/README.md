# Test Files

This directory contains test scripts for the RAG system.

## Test Scripts

### End-to-End Tests
- **`test_e2e_rag.py`** - Complete RAG pipeline test with plutonium document
- **`test_s3_upload_and_query.py`** - S3 integration test with coffee guide

### Component Tests
- **`test_migration.py`** - Supabase migration verification
- **`test_connection.py`** - Supabase connection test
- **`test_supabase.py`** - Supabase operations test
- **`test_hallucination.py`** - LLM hallucination detection test

### Legacy Tests
- **`test_s3_flow.py`** - Original S3 flow test
- **`inspect_qdrant*.py`** - Old Qdrant inspection scripts (deprecated)
- **`run_sql_guide.py`** - SQL initialization helper

## Test Documents
- **`plutonium_overview.docx`** - Sample DOCX for testing
- **`test_coffee_guide.txt`** - Sample TXT for testing
- **`test_python.txt`** - Sample text file

## Running Tests

### Prerequisites
```bash
# Make sure .env is configured
cd /home/parthav/work/rag
source .env  # or use python-dotenv
```

### Run Individual Tests
```bash
# End-to-end RAG test
python tests/test_e2e_rag.py

# S3 integration test
python tests/test_s3_upload_and_query.py

# Hallucination test
python tests/test_hallucination.py
```

### Expected Results
All tests should pass with ✅ indicators. If any test fails, check:
1. Environment variables are set correctly
2. Supabase is initialized (run `init_supabase.sql`)
3. Services are running (if using Docker)

## Test Coverage

- ✅ Document parsing (PDF, DOCX, TXT)
- ✅ Text chunking
- ✅ Embedding generation
- ✅ Supabase vector storage
- ✅ Similarity search
- ✅ Context building
- ✅ LLM answer generation
- ✅ S3 integration
- ✅ Document management (list, delete)
- ✅ Multi-tenant isolation
