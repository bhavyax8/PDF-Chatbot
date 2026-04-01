import os
from langchain_community.vectorstores import FAISS
from src.embeddings import get_embeddings

INDEX_PATH = "faiss_index"
def vector_store(chunks):
    print("[Vector Store] Creating vector store with FAISS.")
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks,embeddings)
    vector_store.save_local(INDEX_PATH)
    print(f"[Vector Store] Vector store saved to {INDEX_PATH}.")
    return vector_store

def load_vector_store():
    print(f"[Vector Store] Loading vector store from {INDEX_PATH}.")
    if not os.path.exists(INDEX_PATH):
       raise FileNotFoundError(
          f"No index found at'/{INDEX_PATH}'"
          "Please upload and index a api first"
        )
    embeddings = get_embeddings()
    return FAISS.load_local(
       INDEX_PATH,embeddings, allow_dangerous_deserialization=True
    )