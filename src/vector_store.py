# src/vector_store.py
import os
import pickle
from dotenv import load_dotenv
load_dotenv()

INDEX_PATH = "faiss_index"
DOCS_PATH  = "faiss_index/docs.pkl"


def build_vector_store(chunks):
    print(f"[VectorStore] Building from {len(chunks)} chunks...")
    import faiss
    import numpy as np
    from src.embeddings import get_embeddings

    os.makedirs(INDEX_PATH, exist_ok=True)

    embeddings_model = get_embeddings()

    # Extract texts
    texts = [c.page_content for c in chunks]

    # Embed all texts at once
    vectors = embeddings_model.embed_documents(texts)
    vectors = np.array(vectors, dtype="float32")

    # Build raw FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save index and original chunks separately
    faiss.write_index(index, f"{INDEX_PATH}/index.faiss")
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"[VectorStore] Saved {len(texts)} vectors.")
    return index, chunks


def load_vector_store():
    import faiss
    import numpy as np
    from src.embeddings import get_embeddings

    if not os.path.exists(f"{INDEX_PATH}/index.faiss"):
        raise FileNotFoundError("No FAISS index found. Upload a PDF first.")

    index = faiss.read_index(f"{INDEX_PATH}/index.faiss")
    with open(DOCS_PATH, "rb") as f:
        chunks = pickle.load(f)

    embeddings_model = get_embeddings()

    # Return a simple retriever object
    class SimpleRetriever:
        def __init__(self, index, chunks, embeddings_model, k=4):
            self.index = index
            self.chunks = chunks
            self.embeddings_model = embeddings_model
            self.k = k

        def get_relevant_documents(self, query):
            import numpy as np
            vec = self.embeddings_model.embed_query(query)
            vec = np.array([vec], dtype="float32")
            _, indices = self.index.search(vec, self.k)
            return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

        def as_retriever(self, **kwargs):
            return self

        def invoke(self, query):
            return self.get_relevant_documents(query)

    return SimpleRetriever(index, chunks, embeddings_model)