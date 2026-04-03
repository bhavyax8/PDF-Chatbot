# app.py
import streamlit as st
import httpx
import base64
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Works both locally (.env file) and on Streamlit Cloud (st.secrets)
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")

API_URL = get_secret("API_URL") or "http://localhost:8000"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI PDF Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS — gradients, bubbles, animations ────────────────────────────────
st.markdown("""
<style>
/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255,255,255,0.1);
}
[data-testid="stSidebar"] * {
    color: #fff !important;
}

/* ── Main content text ── */
.stApp, .stApp p, .stApp label,
.stApp .stMarkdown { color: #f0f0f0 !important; }

/* ── Section headers ── */
.section-title {
    font-size: 13px;
    font-weight: 600;
    color: rgba(255,255,255,0.5) !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 16px 0 8px 0;
}

/* ── Model pill cards ── */
.model-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.model-card:hover {
    background: rgba(255,255,255,0.14);
    border-color: rgba(255,255,255,0.3);
}
.model-card.active {
    background: linear-gradient(135deg,rgba(99,102,241,0.4),rgba(168,85,247,0.4));
    border-color: rgba(168,85,247,0.6);
}
.model-name { font-weight: 600; font-size: 14px; color: #fff; }
.model-desc { font-size: 11px; color: rgba(255,255,255,0.55); margin-top: 2px; }

/* ── Chat bubbles ── */
.chat-wrap { margin-bottom: 16px; }

.bubble-ai {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    max-width: 85%;
    display: inline-block;
    color: #f0f0f0;
    font-size: 14px;
    line-height: 1.6;
    backdrop-filter: blur(8px);
}

.bubble-user {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    max-width: 85%;
    display: inline-block;
    color: #fff;
    font-size: 14px;
    line-height: 1.6;
    float: right;
    clear: both;
}

.bubble-wrap-user { text-align: right; margin-bottom: 16px; }
.bubble-wrap-ai  { text-align: left;  margin-bottom: 16px; }

.meta-ai   { font-size: 11px; color: rgba(255,255,255,0.4);
             margin-top: 5px; margin-left: 4px; }
.meta-user { font-size: 11px; color: rgba(255,255,255,0.4);
             margin-top: 5px; text-align: right; margin-right: 4px; }

/* ── Source badge ── */
.source-badge {
    display: inline-block;
    background: rgba(99,102,241,0.25);
    border: 1px solid rgba(99,102,241,0.5);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    color: #a5b4fc;
    margin-top: 4px;
}

/* ── Typing dots animation ── */
.typing-bubble {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
    padding: 12px 20px;
    display: inline-block;
    backdrop-filter: blur(8px);
}
.dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: rgba(255,255,255,0.6);
    margin: 0 2px;
    animation: bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%,80%,100% { transform: translateY(0);   opacity:0.4; }
    40%          { transform: translateY(-6px); opacity:1;   }
}

/* ── PDF preview panel ── */
.pdf-panel {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px;
    height: 100%;
}
.pdf-panel-title {
    font-size: 13px; font-weight: 600;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

/* ── Chat panel ── */
.chat-panel {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    min-height: 520px;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px dashed rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    padding: 8px !important;
}

/* ── Selectbox + buttons ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #fff !important;
    border-radius: 10px !important;
}
.stButton > button {
    background: linear-gradient(135deg,#6366f1,#a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #fff !important;
    border-radius: 12px !important;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in {
    "messages": [],
    "pdf_name": None,
    "pdf_bytes": None,
    "provider": "gemini",
    "is_typing": False,
    "pdf_page": 1,
    "pdf_total_pages": 1,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Helper: timestamp ──────────────────────────────────────────────────────────
def now():
    return datetime.datetime.now().strftime("%I:%M %p")

# ── Helper: render PDF page as image ──────────────────────────────────────────
def get_pdf_page_count(pdf_bytes):
    """Get total pages using pypdf — no system dependencies needed."""
    try:
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return len(reader.pages)
    except Exception:
        return 1

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📄 AI PDF Chatbot")
    st.markdown("---")

    # API health check
    try:
        r = httpx.get(f"{API_URL}/", timeout=30)
        st.success("✅ API connected")
    except Exception:
        st.error("❌ Start FastAPI first:\nuvicorn api.main:app --reload")
        st.stop()

    # Model selector
    st.markdown('<div class="section-title">Choose AI Model</div>',
                unsafe_allow_html=True)

    models = {
        "gemini":      ("🟣", "Gemini 2.5 Flash", "Google · Free · Fast"),
        "groq":        ("🟡", "Groq Llama3",       "Ultra fast · Free tier"),
        "openai":      ("🟢", "GPT-3.5 Turbo",     "OpenAI · Paid · Best quality"),
        "huggingface": ("🔵", "Llama 3.2 Local",   "Ollama · 100% offline · Free"),
    }

    provider = st.selectbox(
        "Model",
        options=list(models.keys()),
        format_func=lambda k: f"{models[k][0]} {models[k][1]}",
        label_visibility="collapsed"
    )
    st.session_state.provider = provider
    emoji, name, desc = models[provider]
    st.markdown(
        f'<div class="model-card active">'
        f'<div class="model-name">{emoji} {name}</div>'
        f'<div class="model-desc">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # PDF Upload
    st.markdown('<div class="section-title">Upload PDF</div>',
                unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        pdf_bytes = uploaded.read()
        if st.session_state.pdf_name != uploaded.name:
            with st.spinner("Indexing PDF..."):
                files = {"file": (uploaded.name, pdf_bytes, "application/pdf")}
                resp = httpx.post(f"{API_URL}/ingest", files=files, timeout=120)

            if resp.status_code == 200:
                data = resp.json()
                st.session_state.pdf_name   = uploaded.name
                st.session_state.pdf_bytes  = pdf_bytes
                st.session_state.pdf_page   = 1
                st.session_state.messages   = []
                httpx.delete(f"{API_URL}/reset")

                # Get total pages
                st.session_state.pdf_total_pages = get_pdf_page_count(pdf_bytes)

                st.success(f"✅ {data['chunks']} chunks indexed")
            else:
                try:
                    detail = resp.json().get("detail", "Ingestion failed")
                except Exception:
                    detail = f"Server error (status {resp.status_code}). API may be waking up — try again in 30 seconds."
                st.error(detail)
    if st.session_state.pdf_name:
        st.markdown(
            f'<div class="model-card">'
            f'<div class="model-name">📄 {st.session_state.pdf_name}</div>'
            f'<div class="model-desc">'
            f'{st.session_state.pdf_total_pages} pages · {provider}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.pdf_name = None
        st.session_state.pdf_bytes = None
        httpx.delete(f"{API_URL}/reset")
        st.rerun()

# ── MAIN LAYOUT — 2 columns: PDF preview | Chat ────────────────────────────────
col_pdf, col_chat = st.columns([1, 1.4], gap="large")

# ── LEFT: PDF PREVIEW ──────────────────────────────────────────────────────────
with col_pdf:
    st.markdown('<div class="pdf-panel-title">📄 PDF Preview</div>',
                unsafe_allow_html=True)

    if st.session_state.pdf_bytes:
        # Embed PDF directly as base64 iframe — no system libs needed
        b64 = base64.b64encode(st.session_state.pdf_bytes).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="500px" style="border-radius:10px;'
            f'border:1px solid rgba(255,255,255,0.1);"></iframe>',
            unsafe_allow_html=True
        )

        # Source page indicator
        if st.session_state.messages:
            last = st.session_state.messages[-1]
            if last["role"] == "assistant" and last.get("sources"):
                st.markdown(
                    f'<div class="source-badge" style="margin-top:10px;">📖 '
                    f'Answer from pages {last["sources"]}</div>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            '<div style="text-align:center;padding:80px 20px;'
            'color:rgba(255,255,255,0.3);">'
            '<div style="font-size:48px;">📄</div>'
            '<div style="margin-top:12px;font-size:14px;">'
            'Upload a PDF to preview it here</div></div>',
            unsafe_allow_html=True
        )

# ── RIGHT: CHAT ────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown('<div class="pdf-panel-title">💬 Chat</div>',
                unsafe_allow_html=True)

    # Render all messages
    if not st.session_state.messages:
        st.markdown(
            '<div class="bubble-wrap-ai"><div class="bubble-ai">'
            '👋 Hello! Upload a PDF and ask me anything about it.'
            '</div><div class="meta-ai">Now · AI</div></div>',
            unsafe_allow_html=True
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="bubble-wrap-user">'
                f'<div class="bubble-user">{msg["content"]}</div>'
                f'<div class="meta-user">{msg.get("time","")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            sources_html = ""
            if msg.get("sources"):
                sources_html = (
                    f'<br><span class="source-badge">'
                    f'📖 Pages {msg["sources"]} · {msg.get("provider","")}'
                    f'</span>'
                )
            st.markdown(
                f'<div class="bubble-wrap-ai">'
                f'<div class="bubble-ai">{msg["content"]}{sources_html}</div>'
                f'<div class="meta-ai">'
                f'{msg.get("time","")} · {msg.get("provider","")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Typing animation placeholder
    typing_placeholder = st.empty()

    # Chat input
    if user_query := st.chat_input("Ask anything about your PDF..."):
        if not st.session_state.pdf_name:
            st.warning("Please upload a PDF first.")
        else:
            ts = now()
            st.session_state.messages.append({
                "role": "user",
                "content": user_query,
                "time": ts
            })

            # Show typing animation
            typing_placeholder.markdown(
                '<div class="bubble-wrap-ai">'
                '<div class="typing-bubble">'
                '<span class="dot"></span>'
                '<span class="dot"></span>'
                '<span class="dot"></span>'
                '</div></div>',
                unsafe_allow_html=True
            )

            # Call FastAPI
            resp = httpx.post(
                f"{API_URL}/chat",
                json={
                    "question": user_query,
                    "provider": st.session_state.provider,
                    "session_id": "default"
                },
                timeout=60
            )

            typing_placeholder.empty()

            if resp.status_code == 200:
                data = resp.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["answer"],
                    "sources": data["source_pages"],
                    "provider": data["provider"],
                    "time": now()
                })
            else:
                try:
                    detail = resp.json().get('detail', 'Unknown error')
                except Exception:
                    detail = f"Server error (status {resp.status_code}). Try again."
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ Error: {detail}",
                    "time": now()
                })

            st.rerun()
