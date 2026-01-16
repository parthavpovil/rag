-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create knowledge vectors table
CREATE TABLE IF NOT EXISTS knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    vector vector(768),
    text TEXT,
    chunk_index INTEGER,
    source_file TEXT,
    file_type TEXT,
    upload_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on tenant_id for fast filtering
CREATE INDEX IF NOT EXISTS idx_knowledge_vectors_tenant_id 
ON knowledge_vectors(tenant_id);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_knowledge_vectors_vector 
ON knowledge_vectors USING ivfflat (vector vector_cosine_ops)
WITH (lists = 100);

-- Optional: Create index on source_file for file listing
CREATE INDEX IF NOT EXISTS idx_knowledge_vectors_source_file 
ON knowledge_vectors(tenant_id, source_file);

-- Create RPC function for vector similarity search
CREATE OR REPLACE FUNCTION match_knowledge_vectors(
    query_embedding vector(768),
    match_tenant_id text,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    tenant_id text,
    text text,
    chunk_index integer,
    source_file text,
    file_type text,
    upload_timestamp timestamp,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        knowledge_vectors.id,
        knowledge_vectors.tenant_id,
        knowledge_vectors.text,
        knowledge_vectors.chunk_index,
        knowledge_vectors.source_file,
        knowledge_vectors.file_type,
        knowledge_vectors.upload_timestamp,
        1 - (knowledge_vectors.vector <=> query_embedding) as similarity
    FROM knowledge_vectors
    WHERE knowledge_vectors.tenant_id = match_tenant_id
    ORDER BY knowledge_vectors.vector <=> query_embedding
    LIMIT match_count;
END;
$$;

