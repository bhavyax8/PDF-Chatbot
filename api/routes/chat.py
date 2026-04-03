# api/routes/chat.py
from fastapi import APIRouter, HTTPException
from api.models import ChatRequest, ChatResponse

router = APIRouter()
_chain_cache: dict = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from src.vector_store import load_vector_store
    from src.chain import build_chain

    cache_key = f"{request.session_id}_{request.provider}"

    try:
        vector_store = load_vector_store()
    except FileNotFoundError:
        raise HTTPException(status_code=400,
                           detail="No PDF indexed yet. Please upload a PDF first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {str(e)}")

    if cache_key not in _chain_cache:
        try:
            _chain_cache[cache_key] = build_chain(vector_store, request.provider)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chain error: {str(e)}")

    chain = _chain_cache[cache_key]

    try:
        # RetrievalQA uses 'query' not 'question'
        result = chain.invoke({"query": request.question})
        answer = result.get("result", "No answer found.")
        source_docs = result.get("source_documents", [])
        pages = sorted(set(
            doc.metadata.get("page", 0) + 1
            for doc in source_docs
        ))
        return ChatResponse(answer=answer, source_pages=pages, provider=request.provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@router.delete("/reset")
async def reset_chat():
    _chain_cache.clear()
    return {"message": "Chat history cleared."}