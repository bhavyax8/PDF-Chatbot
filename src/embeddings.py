# src/embeddings.py
import os
from dotenv import load_dotenv
load_dotenv()


def get_embeddings():
    """
    openai      → OpenAI ada-002 embeddings (needs API key)
    huggingface → sentence-transformers locally (free, no API needed)
    """
    provider = os.environ.get("LLM_PROVIDER", "huggingface").lower()

    if provider == "openai":
        print("[Embeddings] Using OpenAI embeddings (ada-002)")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    else:
        # Used for both huggingface provider AND as fallback
        print("[Embeddings] Using local sentence-transformers (free)")
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )


