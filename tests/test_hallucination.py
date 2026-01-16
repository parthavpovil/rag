#!/usr/bin/env python3
"""
Test RAG system with multiple queries to verify no hallucination.
Tests both questions that CAN and CANNOT be answered from the document.
"""
import sys
import os

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

from knowledge_svc.services.embedder import embed_query
from knowledge_svc.services.vectordb import search
from knowledge_svc.services.context_builder import build_context
from knowledge_svc.services.llm import generate_answer

print("=" * 70)
print("RAG HALLUCINATION TEST")
print("=" * 70)
print()

# Test queries
test_queries = [
    {
        "question": "What is the atomic number of plutonium?",
        "should_answer": True,
        "expected_info": "94"
    },
    {
        "question": "What spacecraft use plutonium RTGs?",
        "should_answer": True,
        "expected_info": "Cassini, Voyager, Perseverance"
    },
    {
        "question": "What is plutonium's symbol?",
        "should_answer": True,
        "expected_info": "Pu"
    },
    {
        "question": "What is the melting point of plutonium?",
        "should_answer": False,
        "expected_info": "Should say 'not in context' or similar"
    },
    {
        "question": "Who discovered plutonium?",
        "should_answer": False,
        "expected_info": "Should say 'not in context' or similar"
    }
]

for i, test in enumerate(test_queries, 1):
    print(f"Test {i}/{len(test_queries)}")
    print("-" * 70)
    print(f"Question: {test['question']}")
    print(f"Expected: {test['expected_info']}")
    print()
    
    try:
        # Retrieve context
        query_embedding = embed_query(test['question'])
        results = search("test_plutonium", query_embedding, limit=3)
        
        print(f"Retrieved {len(results)} chunks:")
        for j, result in enumerate(results, 1):
            print(f"  {j}. Score: {result['score']:.4f} - {result['text'][:80]}...")
        print()
        
        # Build context and generate answer
        context = build_context(results)
        answer = generate_answer(test['question'], context)
        
        print(f"Answer: {answer}")
        print()
        
        # Check for hallucination indicators
        if not test['should_answer']:
            if any(phrase in answer.lower() for phrase in [
                "don't know", "not provided", "not mentioned", 
                "no information", "cannot answer", "not in the context",
                "based on the provided context"
            ]):
                print("✅ GOOD: Model correctly indicated lack of information")
            else:
                print("⚠️  WARNING: Model may be hallucinating (no disclaimer)")
        else:
            print("✅ Answer provided (verify accuracy manually)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 70)
    print()

print("\n🎯 HALLUCINATION TEST COMPLETE")
print("\nKey Points:")
print("- Answers to questions 1-3 should contain specific facts from document")
print("- Answers to questions 4-5 should indicate information is not available")
print("- If model makes up facts for questions 4-5, it's hallucinating")
