#!/usr/bin/env python3
"""
Quick test script to verify Supabase connection and basic operations.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, '/home/parthav/work/rag')

from knowledge_svc.services.vectordb import (
    get_supabase_client,
    ensure_table,
    insert_dummy_vector,
    search_dummy_vector
)

def test_connection():
    """Test basic Supabase connection."""
    print("🔍 Testing Supabase connection...")
    try:
        client = get_supabase_client()
        print("✅ Supabase client created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False

def test_table_access():
    """Test table accessibility."""
    print("\n🔍 Testing table access...")
    try:
        ensure_table()
        print("✅ Table access verified")
        return True
    except Exception as e:
        print(f"❌ Failed to access table: {e}")
        print("⚠️  Make sure you've run init_supabase.sql in Supabase SQL Editor")
        return False

def test_insert():
    """Test inserting a dummy vector."""
    print("\n🔍 Testing vector insertion...")
    try:
        result = insert_dummy_vector("test_tenant")
        print("✅ Dummy vector inserted successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to insert vector: {e}")
        return False

def test_search():
    """Test vector search."""
    print("\n🔍 Testing vector search...")
    try:
        results = search_dummy_vector("test_tenant")
        print(f"✅ Search completed, found {len(results)} results")
        return True
    except Exception as e:
        print(f"❌ Failed to search: {e}")
        print("⚠️  Make sure the match_knowledge_vectors RPC function exists in Supabase")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Supabase Migration Test")
    print("=" * 60)
    
    tests = [
        test_connection,
        test_table_access,
        test_insert,
        test_search
    ]
    
    results = []
    for test in tests:
        results.append(test())
        if not results[-1]:
            print(f"\n⚠️  Test failed, stopping here")
            break
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(tests)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n🎉 All tests passed! Supabase migration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
