# src/embeddings.py
import os
from dotenv import load_dotenv
load_dotenv()


def get_embeddings():
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()

    if provider == "openai":
        print("[Embeddings] Using OpenAI embeddings")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    elif provider == "gemini":
        print("[Embeddings] Using Google Gemini embeddings (free)")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    elif provider == "groq":
        # Groq has no embeddings API — use Gemini as fallback
        print("[Embeddings] Groq has no embeddings — using Gemini embeddings")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    else:
        # huggingface / local — use lightweight local model
        print("[Embeddings] Using local sentence-transformers")
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )