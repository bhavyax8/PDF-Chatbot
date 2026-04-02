# src/chain.py
import os
from dotenv import load_dotenv
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

load_dotenv()

# Custom prompt — answers strictly from PDF content
CUSTOM_PROMPT = PromptTemplate(
    input_variables=["context", "question", "chat_history"],
    template="""You are a helpful assistant that answers questions strictly 
based on the provided PDF document.

Use ONLY the context below to answer. Be direct and confident.
If the answer is clearly in the context, state it without hedging.
If the answer is genuinely not in the context, say: 
"This information is not in the document."

Previous conversation:
{chat_history}

Relevant excerpts from the PDF:
{context}

Question: {question}

Answer:"""
)


def get_llm(provider: str = None):
    """
    Returns the correct LLM based on provider param or LLM_PROVIDER in .env
    Supports: openai | gemini | groq | huggingface
    """
    # Use passed provider or fall back to .env
    provider = (provider or os.environ.get("LLM_PROVIDER", "gemini")).lower()
    print(f"[Chain] Loading LLM provider: {provider}")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",   # fast + free tier
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.1-8b-instant",     # fast, free tier, great quality
            temperature=0.1,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    elif provider == "huggingface":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="llama3.2",
            temperature=0.1
        )

    else:
        raise ValueError(
            f"Unknown provider: '{provider}'. "
            "Use: openai | gemini | groq | huggingface"
        )


def build_chain(vector_store, provider: str = None):
    """
    Builds ConversationalRetrievalChain with memory.
    Provider can be passed directly or read from environment.
    """
    llm = get_llm(provider)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": CUSTOM_PROMPT},
        verbose=False
    )
    print(f"[Chain] RAG chain ready with provider: {provider}")
    return chain