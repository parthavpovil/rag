# Supabase Migration - Setup Instructions

## Step 1: Run SQL Initialization in Supabase

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Click on **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy and paste the contents of `knowledge_svc/init_supabase.sql`
6. Click **Run** (or press Ctrl+Enter)

You should see success messages for:
- ✅ pgvector extension enabled
- ✅ knowledge_vectors table created
- ✅ Indexes created
- ✅ match_knowledge_vectors function created

## Step 2: Verify Table Creation

1. Click on **Table Editor** (left sidebar)
2. You should see `knowledge_vectors` table
3. Click on it to verify the schema

## Step 3: Install Dependencies

```bash
cd /home/parthav/work/rag
pip install -r knowledge_svc/requirements.txt
```

## Step 4: Test the Service

Start the service:
```bash
python -m uvicorn knowledge_svc.main:app --reload
```

Or use Docker:
```bash
docker-compose up --build
```

## What Changed?

- ❌ **Removed**: Qdrant (no more Docker container needed)
- ✅ **Added**: Supabase pgvector (managed PostgreSQL)
- 🔄 **Changed**: `vectordb.py` now uses Supabase client
- 📦 **Updated**: Dependencies in `requirements.txt`

## Next Steps

After running the SQL initialization, test the upload and query endpoints to verify everything works!
