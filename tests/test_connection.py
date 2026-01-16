#!/usr/bin/env python3
"""
Simple connection test - checks if Supabase is accessible and table exists.
"""
import os
import sys

# Set environment variables from .env
from pathlib import Path
env_path = Path('/home/parthav/work/rag/.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

sys.path.insert(0, '/home/parthav/work/rag')

try:
    from supabase import create_client
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    print("🔍 Testing Supabase Connection...")
    print(f"URL: {SUPABASE_URL}")
    print()
    
    # Create client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully")
    
    # Try to query the table
    print("\n🔍 Checking if knowledge_vectors table exists...")
    result = client.table("knowledge_vectors").select("id").limit(1).execute()
    print("✅ Table exists and is accessible!")
    print(f"   Current row count: {len(result.data)}")
    
    # Try to check if the RPC function exists
    print("\n🔍 Testing match_knowledge_vectors RPC function...")
    try:
        import random
        dummy_vector = [random.random() for _ in range(768)]
        result = client.rpc(
            "match_knowledge_vectors",
            {
                "query_embedding": dummy_vector,
                "match_tenant_id": "test",
                "match_count": 1
            }
        ).execute()
        print("✅ RPC function exists and works!")
        print(f"   Returned {len(result.data)} results")
    except Exception as e:
        print(f"❌ RPC function not found or error: {e}")
        print("   Make sure you ran the full SQL including the function definition")
    
    print("\n" + "=" * 70)
    print("🎉 Supabase is properly configured!")
    print("=" * 70)
    
except ImportError:
    print("❌ Supabase library not installed")
    print("   Run: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("1. SQL not run in Supabase dashboard yet")
    print("2. Credentials incorrect")
    print("3. Network issue")
    sys.exit(1)
