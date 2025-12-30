import os
from openai import OpenAI

# Initialize OpenAI client
# Assumes OPENAI_API_KEY is set in environment variables
_client = None

def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. LLM calls will fail.")
        _client = OpenAI(api_key=api_key)
    return _client

def generate_answer(query: str, context: str) -> str:
    client = get_openai_client()
    
    system_prompt = (
        "You are a helpful assistant for a RAG (Retrieval-Augmented Generation) system. "
        "Your task is to answer the user's question strictly based on the provided context. "
        "If the answer is not in the context, say 'I don't know' or 'The provided context does not contain this information'. "
        "Do not hallucinate or use outside knowledge."
    )
    
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or gpt-4o if available
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0, # Low temperature for factual answers
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return f"Error generating answer: {str(e)}"
