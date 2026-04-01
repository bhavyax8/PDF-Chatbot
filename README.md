# 📄 AI PDF Chatbot

An end-to-end RAG (Retrieval-Augmented Generation) chatbot that lets you
upload any PDF and ask questions about it in natural language.

Built as a portfolio project after completing the Coursera GenAI with LLMs
and LangChain for Application Development certifications.

---

## Features

- Upload any PDF and chat with it instantly
- Multi-turn conversation with memory (follow-up questions work)
- Switch between **OpenAI GPT-3.5** and **local Llama 3.2 (free)** at runtime
- Shows which PDF pages each answer came from
- Answers strictly from document content — no hallucination

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM (paid) | OpenAI GPT-3.5-turbo |
| LLM (free) | Llama 3.2 via Ollama (local) |
| Embeddings | OpenAI ada-002 / sentence-transformers |
| Vector store | FAISS |
| Framework | LangChain |
| Language | Python 3.11 |

---

## Architecture
```
PDF → PyPDF loader → RecursiveCharacterTextSplitter
    → Embeddings (OpenAI or HuggingFace)
    → FAISS vector store
    → ConversationalRetrievalChain + memory
    → Streamlit chat UI
```

---

## Setup & Run

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed (for free local LLM)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-pdf-chatbot.git
cd ai-pdf-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
# Then edit .env and add your API keys
```

### 5. Pull the local LLM (for free tier)
```bash
ollama pull llama3.2
```

### 6. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Usage

1. Select your LLM provider in the sidebar (HuggingFace = free, OpenAI = better quality)
2. Upload any PDF using the sidebar
3. Ask questions in the chat box
4. Source page numbers appear below each answer

---

## Project Structure
```
ai-pdf-chatbot/
├── src/
│   ├── ingestion.py      # PDF loading and chunking
│   ├── embeddings.py     # Embedding model switcher
│   ├── vector_store.py   # FAISS build and load
│   └── chain.py          # RAG chain with memory
├── app.py                # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

---

## What I learned

- How RAG (Retrieval-Augmented Generation) works end to end
- Chunking strategies and their effect on retrieval quality
- Vector similarity search with FAISS
- LangChain's ConversationalRetrievalChain and memory management
- Running open-source LLMs locally with Ollama
- Building and deploying ML apps with Streamlit
