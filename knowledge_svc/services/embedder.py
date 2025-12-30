from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en-v1.5"
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Model loaded.")
    return _model

def embed_document(text: str) -> list[float]:
    model = get_model()
    # BGE v1.5: No instruction needed for documents
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def embed_query(text: str) -> list[float]:
    model = get_model()
    # BGE v1.5: Recommended instruction for queries
    instruction = "Represent this sentence for searching relevant passages: "
    embedding = model.encode(instruction + text, normalize_embeddings=True)
    return embedding.tolist()
