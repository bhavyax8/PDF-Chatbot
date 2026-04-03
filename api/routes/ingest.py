# api/routes/ingest.py
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


@router.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")

    from src.ingestion import load_and_split
    from src.vector_store import build_vector_store

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunks = load_and_split(tmp_path)
        build_vector_store(chunks)   # returns (index, chunks) but we don't need it here
        return {
            "message": "PDF indexed successfully.",
            "chunks": len(chunks),
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)