from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes.ingest import router as ingest_router
from api.routes.chat import router as chat_router
from api.models import HealthResponse

app = FastAPI(
    title="AI PDF Chatbot API",
    description="RAG pipeline with OpenAI, Gemini, Groq and Ollama support",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for now, tighten after Streamlit URL is known
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(chat_router, tags=["Chat"])


@app.get("/", response_model=HealthResponse)
@app.head("/")  # ← this fixes Render's health check ping
async def health_check():
    return HealthResponse(
        status="running",
        available_providers=["openai", "gemini", "groq", "huggingface"]
    )