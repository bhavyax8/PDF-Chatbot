# api/routes/ingest.py
# Handles PDF upload at POST /ingest
# Streamlit sends the PDF file here, we chunk + embed + store it

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.models import IngestResponse
from src.ingestion import load_and_split
from src.vector_store import vector_store

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file, chunks it, embeds it, saves to FAISS.
    Called once when user uploads a PDF in Streamlit.
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    print(f"[Ingest] Received file: {file.filename}")

    # Save uploaded file to a temporary location on disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Run ingestion pipeline
        chunks = load_and_split(tmp_path)
        vector_store(chunks)
        print(f"[Ingest] Done. {len(chunks)} chunks stored.")

        return IngestResponse(
            message="PDF indexed successfully.",
            chunks=len(chunks),
            filename=file.filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Always clean up temp file
        os.unlink(tmp_path)