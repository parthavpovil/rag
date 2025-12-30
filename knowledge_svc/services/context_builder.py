def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    
    context_parts = []
    for chunk in chunks:
        text = chunk.get("text", "")
        source = chunk.get("source", "unknown")
        
        # Simple formatting
        part = f"Source: {source}\nContent: {text}"
        context_parts.append(part)
    
    return "\n\n---\n\n".join(context_parts)
