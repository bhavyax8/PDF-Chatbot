# src/chain.py
import os
from dotenv import load_dotenv
load_dotenv()


def get_llm(provider: str = None):
    provider = (provider or os.environ.get("LLM_PROVIDER", "gemini")).lower()
    print(f"[Chain] Provider: {provider}")

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
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama3-8b-8192",
            temperature=0.1,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    else:
        from langchain_ollama import ChatOllama
        return ChatOllama(model="llama3.2", temperature=0.1)


def build_chain(retriever, provider: str = None):
    llm = get_llm(provider)

    PROMPT = """You are a helpful assistant. Answer using ONLY the context below.
If the answer is not in the context, say "This information is not in the document."

Context:
{context}

Question: {question}

Answer:"""

    def chain_fn(inputs):
        question = inputs["query"]
        docs = retriever.get_relevant_documents(question)
        context = "\n\n".join(d.page_content for d in docs)
        prompt = PROMPT.format(context=context, question=question)

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content if hasattr(response, "content") else str(response)

        return {
            "result": answer,
            "source_documents": docs
        }

    print(f"[Chain] Ready with provider: {provider}")
    return chain_fn