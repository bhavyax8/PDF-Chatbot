# app.py
# Main Streamlit application — run this with: streamlit run app.py

import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

from src.ingestion import load_and_split
from src.vector_store import vector_store
from src.chain import build_chain

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI PDF Chatbot",
    page_icon="📄",
    layout="wide"
)

# ── Session state (persists across reruns) ──────────────────────────────────────
if "chain" not in st.session_state:
    st.session_state.chain = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📄 AI PDF Chatbot")
    st.markdown("---")

    # LLM provider switcher — reads from .env but lets user override in UI
    provider = st.radio(
        "LLM Provider",
        options=["openai", "huggingface"],
        index=0 if os.getenv("LLM_PROVIDER", "huggingface") == "huggingface" else 1,
        help="OpenAI: better quality, costs ~$0.01/chat\nHuggingFace: free, slightly slower"
    )
    # Write the chosen provider back to environment so chain.py and embeddings.py pick it up
    os.environ["LLM_PROVIDER"] = provider

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file:
        # Only re-index if it's a new file
        if st.session_state.pdf_name != uploaded_file.name:
            with st.spinner(f"Indexing '{uploaded_file.name}'..."):
                # Save uploaded file to a temp location on disk
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                # Run the full pipeline
                chunks = load_and_split(tmp_path)
                vector_store = vector_store(chunks)
                st.session_state.chain = build_chain(vector_store)
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.messages = []  # clear old chat on new PDF

                os.unlink(tmp_path)  # delete temp file

            st.success(f"✅ Indexed {uploaded_file.name}")

    if st.session_state.pdf_name:
        st.info(f"Active PDF: {st.session_state.pdf_name}")

    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.chain = None
        st.session_state.pdf_name = None
        st.rerun()

# ── Main chat area ───────────────────────────────────────────────────────────────
st.header("Chat with your PDF")

if not st.session_state.pdf_name:
    st.info("👈 Upload a PDF in the sidebar to get started.")

# Display all past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            st.caption(f"📖 Sources: pages {msg['sources']}")

# Chat input
if user_query := st.chat_input("Ask anything about your PDF..."):
    if not st.session_state.chain:
        st.warning("Please upload a PDF first.")
    else:
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        # Get AI answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.chain({"question": user_query})
                answer = result["answer"]
                source_docs = result.get("source_documents", [])

                # Extract page numbers from source documents
                pages = sorted(set(
                    doc.metadata.get("page", 0) + 1  # +1 because pages are 0-indexed
                    for doc in source_docs
                ))

            st.write(answer)
            if pages:
                st.caption(f"📖 Sources: pages {pages}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": pages
        })
