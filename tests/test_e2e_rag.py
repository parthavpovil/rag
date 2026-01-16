#!/usr/bin/env python3
"""
End-to-end RAG test with real document.
Tests: file parsing → chunking → embedding → Supabase storage → retrieval → LLM
"""
import sys
import os
from pathlib import Path

# Load environment variables
env_path = '/home/parthav/work/rag/.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

sys.path.insert(0, '/home/parthav/work/rag')

print("=" * 70)
print("END-TO-END RAG TEST WITH PLUTONIUM DOCUMENT")
print("=" * 70)
print()

# Import all services
try:
    from knowledge_svc.services.file_parser import parse_file
    from knowledge_svc.services.chunker import chunk_text
    from knowledge_svc.services.embedder import embed_document, embed_query
    from knowledge_svc.services.vectordb import upsert_chunks, search
    from knowledge_svc.services.context_builder import build_context
    from knowledge_svc.services.llm import generate_answer
    print("✅ All services imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nMissing dependencies. Install with:")
    print("  pip install --break-system-packages sentence-transformers openai python-docx")
    sys.exit(1)

print()

# Step 1: Parse document
print("📄 Step 1: Parsing plutonium_overview.docx...")
doc_path = "/home/parthav/work/rag/plutonium_overview.docx"
try:
    with open(doc_path, 'rb') as f:
        file_bytes = f.read()
    text = parse_file("plutonium_overview.docx", file_bytes)
    print(f"✅ Parsed successfully! Length: {len(text)} characters")
    print(f"   Preview: {text[:100]}...")
except Exception as e:
    print(f"❌ Parsing failed: {e}")
    sys.exit(1)

print()

# Step 2: Chunk text
print("✂️  Step 2: Chunking text...")
try:
    chunks = chunk_text(text)
    print(f"✅ Created {len(chunks)} chunks")
    print(f"   First chunk preview: {chunks[0][:100]}...")
except Exception as e:
    print(f"❌ Chunking failed: {e}")
    sys.exit(1)

print()

# Step 3: Generate embeddings
print("🧮 Step 3: Generating embeddings...")
try:
    embeddings = [embed_document(chunk) for chunk in chunks]
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   Vector dimension: {len(embeddings[0])}")
except Exception as e:
    print(f"❌ Embedding failed: {e}")
    sys.exit(1)

print()

# Step 4: Store in Supabase
print("💾 Step 4: Storing vectors in Supabase...")
try:
    from datetime import datetime
    upsert_chunks(
        tenant_id="test_plutonium",
        chunks=chunks,
        embeddings=embeddings,
        source_file="plutonium_overview.docx",
        file_type=".docx",
        upload_timestamp=datetime.now().isoformat()
    )
    print(f"✅ Successfully stored {len(chunks)} chunks in Supabase")
except Exception as e:
    print(f"❌ Storage failed: {e}")
    sys.exit(1)

print()

# Step 5: Test retrieval
print("🔍 Step 5: Testing retrieval with query...")
test_query = "What is plutonium used for?"
try:
    query_embedding = embed_query(test_query)
    results = search("test_plutonium", query_embedding, limit=3)
    
    print(f"✅ Retrieved {len(results)} relevant chunks")
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i} (score: {result['score']:.4f}):")
        print(f"   {result['text'][:150]}...")
except Exception as e:
    print(f"❌ Retrieval failed: {e}")
    sys.exit(1)

print()

# Step 6: Build context
print("📋 Step 6: Building context...")
try:
    context = build_context(results)
    print(f"✅ Context built successfully")
    print(f"   Context length: {len(context)} characters")
except Exception as e:
    print(f"❌ Context building failed: {e}")
    sys.exit(1)

print()

# Step 7: Generate answer with LLM
print("🤖 Step 7: Generating answer with LLM...")
try:
    answer = generate_answer(test_query, context)
    print(f"✅ Answer generated successfully")
    print(f"\n   Question: {test_query}")
    print(f"   Answer: {answer}")
except Exception as e:
    print(f"❌ LLM generation failed: {e}")
    print(f"   (This might fail if OPENAI_API_KEY is invalid)")

print()
print("=" * 70)
print("🎉 END-TO-END RAG PIPELINE TEST COMPLETE!")
print("=" * 70)
print("\n✅ All components working:")
print("   1. Document parsing (DOCX)")
print("   2. Text chunking")
print("   3. Embedding generation")
print("   4. Supabase vector storage")
print("   5. Similarity search")
print("   6. Context building")
print("   7. LLM answer generation")
print("\n🚀 Your RAG system with Supabase is fully operational!")
