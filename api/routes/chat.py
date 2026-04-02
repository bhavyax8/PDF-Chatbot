# api/routes/chat.py
# Handles chat at POST /chat
# Streamlit sends question + provider, we return answer + source pages

from fastapi import APIRouter, HTTPException
from api.models import ChatRequest, ChatResponse
from src.vector_store import load_vector_store
from src.chain import build_chain

router = APIRouter()

# Store chains in memory per session
# Simple dict works for single-user portfolio demo
_chain_cache: dict = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Accepts a question and provider name.
    Loads the FAISS index, builds the RAG chain, returns answer.
    """
    print(f"[Chat] Question: {request.question} | Provider: {request.provider}")

    # Cache key = session + provider (rebuild if provider changes)
    cache_key = f"{request.session_id}_{request.provider}"

    try:
        # Load vector store from disk
        vector_store = load_vector_store()
    except FileNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="No PDF indexed yet. Please upload a PDF first."
        )

    # Build or reuse cached chain
    if cache_key not in _chain_cache:
        print(f"[Chat] Building new chain for key: {cache_key}")
        _chain_cache[cache_key] = build_chain(vector_store, request.provider)

    chain = _chain_cache[cache_key]

    try:
        result = chain({"question": request.question})
        answer = result["answer"]
        source_docs = result.get("source_documents", [])

        # Extract unique page numbers (1-indexed)
        pages = sorted(set(
            doc.metadata.get("page", 0) + 1
            for doc in source_docs
        ))

        return ChatResponse(
            answer=answer,
            source_pages=pages,
            provider=request.provider
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset")
async def reset_chat():
    """Clears all cached chains — call when user uploads a new PDF."""
    _chain_cache.clear()
    return {"message": "Chat history cleared."}