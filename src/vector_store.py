# src/vector_store.py
import os
from dotenv import load_dotenv
load_dotenv()

INDEX_PATH = "faiss_index"


def vector_store(chunks):
    print(f"[VectorStore] Building FAISS index from {len(chunks)} chunks...")

    # Import inside function to avoid module-level conflicts
    try:
        from langchain_community.vectorstores import FAISS
    except ImportError:
        from langchain_classic.vectorstores import FAISS

    from src.embeddings import get_embeddings
    embeddings = get_embeddings()

    # Extract text and metadata separately — most reliable method
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    vector_store = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    vector_store.save_local(INDEX_PATH)
    print(f"[VectorStore] Saved {len(texts)} vectors to '{INDEX_PATH}/'")
    return vector_store


def load_vector_store():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"No FAISS index at '{INDEX_PATH}/'. Upload a PDF first."
        )

    try:
        from langchain_community.vectorstores import FAISS
    except ImportError:
        from langchain_classic.vectorstores import FAISS

    from src.embeddings import get_embeddings
    embeddings = get_embeddings()

    print("[VectorStore] Loading FAISS index...")
    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )