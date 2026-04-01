# src/chain.py
import os
from dotenv import load_dotenv
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory

load_dotenv()


def get_llm():
    """
    Returns the correct LLM based on LLM_PROVIDER in .env

    openai      → GPT-3.5-turbo (needs API key + credits)
    huggingface → Llama 3.2 running locally via Ollama (100% free, no API key)
    """
    provider = os.environ.get("LLM_PROVIDER", "huggingface").lower()

    if provider == "openai":
        print("[Chain] Using OpenAI GPT-3.5-turbo")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    elif provider == "huggingface":
        print("[Chain] Using Llama 3.2 locally via Ollama (free)")
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="llama3.2",
            temperature=0.1,
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'. Use 'openai' or 'huggingface'.")


def build_chain(vector_store):
    """
    Builds the full RAG chain with a custom prompt and conversation memory.
    """
    from langchain_core.prompts import PromptTemplate

    # This prompt tells the LLM to answer only from the PDF content
    custom_prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template="""You are a helpful assistant that answers questions strictly based on the provided PDF document.

Use ONLY the context below to answer. Be direct and confident.
If the answer is clearly in the context, state it without hedging.
If the answer is genuinely not in the context, say "This information is not in the document."

Previous conversation:
{chat_history}

Relevant excerpts from the PDF:
{context}

Question: {question}

Answer:"""
    )

    llm = get_llm()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
        verbose=False
    )

    print("[Chain] RAG chain ready.")
    return chain