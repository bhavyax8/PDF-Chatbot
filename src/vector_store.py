# src/vector_store.py
import os
from dotenv import load_dotenv
load_dotenv()

INDEX_PATH = "faiss_index"


def vector_store(chunks):
    print(f"[VectorStore] Building from {len(chunks)} chunks...")

    from langchain_community.vectorstores import FAISS
    from src.embeddings import get_embeddings

    embeddings = get_embeddings()

    # Use from_documents — correct in langchain 0.3.x
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(INDEX_PATH)

    print(f"[VectorStore] Saved to '{INDEX_PATH}/'")
    return vector_store


def load_vector_store():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            "No FAISS index found. Upload a PDF first."
        )

    from langchain_community.vectorstores import FAISS
    from src.embeddings import get_embeddings

    embeddings = get_embeddings()
    print("[VectorStore] Loading FAISS index...")

    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )