# api/main.py — lightweight startup, lazy imports
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI PDF Chatbot API",
    description="RAG pipeline with Gemini, Groq, OpenAI support",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health check — must respond instantly ──────────────────────────────────────
@app.get("/")
@app.head("/")
async def health_check():
    return {
        "status": "running",
        "available_providers": ["openai", "gemini", "groq", "huggingface"]
    }

# ── Register routers AFTER app is created ─────────────────────────────────────
# Import routes here (not at top of file) to keep startup fast
from api.routes.ingest import router as ingest_router
from api.routes.chat import router as chat_router

app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(chat_router, tags=["Chat"])