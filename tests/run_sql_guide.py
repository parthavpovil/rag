#!/usr/bin/env python3
"""
Quick script to copy the SQL to clipboard for easy pasting into Supabase.
Also provides step-by-step instructions.
"""

print("=" * 70)
print("SUPABASE SQL INITIALIZATION - STEP BY STEP")
print("=" * 70)
print()
print("📋 STEP 1: Copy the SQL")
print("-" * 70)
print("The SQL content is in: knowledge_svc/init_supabase.sql")
print()

# Read and display the SQL
with open('/home/parthav/work/rag/knowledge_svc/init_supabase.sql', 'r') as f:
    sql_content = f.read()

print("SQL TO RUN:")
print("=" * 70)
print(sql_content)
print("=" * 70)
print()

print("🌐 STEP 2: Open Supabase Dashboard")
print("-" * 70)
print("1. Go to: https://supabase.com/dashboard")
print("2. Select your project (vvqlscapsbmybzivorye)")
print("3. Click 'SQL Editor' in the left sidebar")
print("4. Click 'New Query'")
print()

print("📝 STEP 3: Run the SQL")
print("-" * 70)
print("1. Copy the SQL above")
print("2. Paste it into the SQL Editor")
print("3. Click 'Run' (or press Ctrl+Enter)")
print()

print("✅ STEP 4: Verify Success")
print("-" * 70)
print("You should see success messages for:")
print("  - pgvector extension enabled")
print("  - knowledge_vectors table created")
print("  - Indexes created")
print("  - match_knowledge_vectors function created")
print()

print("🔍 STEP 5: Check Table Editor")
print("-" * 70)
print("1. Click 'Table Editor' in the left sidebar")
print("2. You should see 'knowledge_vectors' table")
print()

print("=" * 70)
print("After completing these steps, come back here and we'll test!")
print("=" * 70)
