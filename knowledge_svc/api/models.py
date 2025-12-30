from pydantic import BaseModel

class UploadRequest(BaseModel):
    tenant_id: str
    raw_text: str

class UploadResponse(BaseModel):
    status: str
    message: str | None = None

class QueryRequest(BaseModel):
    tenant_id: str
    query: str

class QueryResponse(BaseModel):
    status: str
    answer: str | None = None
    retrieved_chunks: list[dict] | None = None

