# api/models.py
# Defines the shape of data going in and out of FastAPI endpoints.
# Pydantic validates every request automatically.

from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """What Streamlit sends when user asks a question."""
    question: str
    provider: str = "gemini"        # which LLM to use
    session_id: str = "default"     # future: support multiple users


class ChatResponse(BaseModel):
    """What FastAPI sends back after getting an answer."""
    answer: str
    source_pages: List[int] = []    # which PDF pages were used
    provider: str                   # which LLM answered


class IngestResponse(BaseModel):
    """Response after uploading and indexing a PDF."""
    message: str
    chunks: int                     # how many chunks were created
    filename: str


class HealthResponse(BaseModel):
    """Simple health check response."""
    status: str
    available_providers: List[str]