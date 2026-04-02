# api/main.py
# Main FastAPI application — run with: uvicorn api.main:app --reload
# Visit http://localhost:8000/docs for interactive API documentation

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.ingest import router as ingest_router
from api.routes.chat import router as chat_router
from api.models import HealthResponse

app = FastAPI(
    title="AI PDF Chatbot API",
    description="RAG pipeline with OpenAI, Gemini, Groq and Ollama support",
    version="2.0.0"
)

# Allow Streamlit (port 8501) to talk to FastAPI (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(chat_router, tags=["Chat"])


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Quick check that the API is running."""
    return HealthResponse(
        status="running",
        available_providers=["openai", "gemini", "groq", "huggingface"]
    )