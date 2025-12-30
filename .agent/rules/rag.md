---
trigger: always_on
---

Knowledge Service (knowledge-svc) – Architecture Design

Overview
--------
The knowledge-svc is a standalone, stateless service responsible for Retrieval-Augmented Generation (RAG).
Its job is to ingest tenant knowledge, retrieve relevant information, and generate answers using an LLM.
It does not handle authentication, authorization, or UI logic.

High-Level Responsibility
-------------------------
- Ingest and process tenant knowledge
- Convert text into embeddings
- Store and retrieve vectors
- Build context for the LLM
- Generate answers strictly from retrieved context

------------------------------------------------------------

1. Input Boundary
-----------------
Source:
- Backend / API Gateway

Input:
- tenant_id
- raw_text (upload flow) OR query (question flow)

Assumptions:
- Authentication and tenant validation are already done
- knowledge-svc trusts the backend

------------------------------------------------------------

2. Ingestion Path (Upload Flow)
------------------------------

2.1 Text Intake
- Receives plain UTF-8 text
- No file parsing in MVP (text only)

Output:
- Single large text blob

2.2 Chunking
- Splits text into fixed-size overlapping chunks
- Implemented inside knowledge-svc

Output:
- List of text chunks

2.3 Embedding (Document Side)
- Uses embedding model: BAAI/bge-base-en-v1.5
- Runs locally via SentenceTransformers
- Prefix applied for document embeddings
- Vectors are normalized

Output:
- Vector (768-dim float array) + payload

2.4 Vector Storage
- Uses Qdrant (self-hosted)
- One collection per tenant

Collection format:
- tenant_<tenant_id>_docs

Stored data:
- vector
- original chunk text
- metadata (source_id, chunk_id)

------------------------------------------------------------

3. Query Path (Question Flow)
----------------------------

3.1 Query Intake
- Receives user question + tenant_id

3.2 Query Embedding
- Uses same embedding model as ingestion
- Prefix applied for query embeddings
- Output is a normalized vector

3.3 Retrieval (Similarity Search)
- knowledge-svc sends query vector to Qdrant
- Qdrant performs cosine similarity search
- Returns top-K most relevant chunks

Output:
- Ranked list of chunks with similarity scores

------------------------------------------------------------

4. Context Builder
------------------

4.1 Context Selection
- Select top N retrieved chunks

4.2 Context Cleaning
- Remove duplicates
- Trim excessive length
- Normalize formatting

4.3 Context Assembly
- Combine chunks into a single context block

Purpose:
- Provide clean, relevant knowledge to the LLM

------------------------------------------------------------

5. LLM Generation
-----------------

5.1 Prompt Construction
- Static system instruction
- Dynamic context block
- User query

5.2 LLM Call
- Uses external LLM (OpenAI initially)
- LLM only generates language

5.3 Output
- Final answer text
- Returned to backend

------------------------------------------------------------

Component Responsibility Summary
--------------------------------
- knowledge-svc: Orchestration
- Chunker: Text splitting
- Embedder: Text to vectors
- Vector DB (Qdrant): Similarity search
- Context Builder: Context preparation
- LLM: Answer generation

------------------------------------------------------------

Architectural Guarantees
------------------------
- Stateless service
- One vector collection per tenant
- Same embedding model for docs and queries
- No cross-tenant data access
- No hidden business logic inside the LLM


the plan
PHASE 1 — Skeleton service (no AI yet)
Goal

Service runs, accepts requests, does nothing smart yet.

Build

Create repo / service folder

Basic HTTP server

Health endpoint

Example endpoints:

GET  /health
POST /upload
POST /query


At this stage:

/upload just logs input

/query just returns "not implemented"

👉 No embeddings, no DB yet

PHASE 2 — Vector DB setup (Qdrant)
Goal

Vector DB is running and reachable.

Build

Run Qdrant via Docker

Create client inside knowledge-svc

Add:

create collection

insert vector (dummy)

search vector (dummy)

Test:

Insert fake vectors

Search returns results

👉 Still no real embeddings

PHASE 3 — Embedding layer (isolated)
Goal

Convert text → vector locally.

Build

Add embedding module

Load bge-base-en-v1.5

Implement two functions:

embed_document(text)

embed_query(text)

Both return []float.

Test:

Same text → same vector

Query & doc vectors have correct size

👉 No Qdrant yet. Just embeddings.

PHASE 4 — Chunking (simple, correct)
Goal

Split text safely.

Build

Implement chunker:

fixed size

overlap

Input: large string

Output: []string

Test:

Large text → multiple chunks

No empty chunks

👉 Still no DB writes.

PHASE 5 — Ingestion path (UPLOAD → STORE)
Goal

End-to-end upload pipeline works.

Build flow
/upload
  → chunk text
  → embed each chunk
  → store in Qdrant (tenant collection)


What to implement:

Create collection if not exists

Store:

vector

chunk text

metadata

Test:

Upload text

Check Qdrant → vectors exist

👉 At this point, data is indexed.

PHASE 6 — Retrieval path (QUERY → CHUNKS)
Goal

Search works correctly.

Build flow
/query
  → embed query
  → search Qdrant
  → return top-K chunks (raw)


Do NOT call LLM yet.

Test:

Ask a question

Returned chunks are relevant

👉 This proves semantic search works.

PHASE 7 — Context Builder
Goal

Prepare clean context.

Build

Take retrieved chunks

Deduplicate

Trim length

Combine into single string

Test:

Context is readable

Not too long

No garbage

👉 Still no LLM.

PHASE 8 — LLM integration (final step)
Goal

Generate final answers.

Build flow
/query
  → embed query
  → retrieve chunks
  → build context
  → call LLM
  → return answer


Add:

System prompt

Context injection

User question

Test:

Answer uses only provided context

Ask something not in docs → “I don’t know”

🎉 Now RAG is complete.