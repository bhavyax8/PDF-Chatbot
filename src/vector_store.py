# src/vector_store.py
import os
from langchain_community.vectorstores import FAISS
from src.embeddings import get_embeddings

INDEX_PATH = "faiss_index"


def vector_store(chunks):
    """
    Takes chunks, embeds them, saves FAISS index to disk.
    """
    print(f"[VectorStore] Building FAISS index from {len(chunks)} chunks...")
    embeddings = get_embeddings()

    # from_documents is the correct method in all LangChain versions
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings      # note: keyword is 'embedding' not 'embeddings'
    )

    vector_store.save_local(INDEX_PATH)
    print(f"[VectorStore] Saved to '{INDEX_PATH}/'")
    return vector_store


def load_vector_store():
    """
    Loads saved FAISS index from disk.
    """
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"No FAISS index at '{INDEX_PATH}/'. Upload a PDF first."
        )
    print("[VectorStore] Loading FAISS index...")
    embeddings = get_embeddings()
    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )