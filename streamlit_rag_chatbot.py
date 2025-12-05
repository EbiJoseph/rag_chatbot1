import streamlit as st
import requests
import os
import shutil

# -----------------------------------------------------------
# Page config (must be first Streamlit call)
# -----------------------------------------------------------
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="💬",
    layout="wide",
)

# Small style tweak – wider sidebar
st.markdown(
    """
    <style>
        div[data-testid='stSidebar'] > div:first-child {
            width: 340px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------
# Directories
# -----------------------------------------------------------
UPLOAD_DIR = "data/uploaded"
EMBEDDED_DIR = "data/embedded"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EMBEDDED_DIR, exist_ok=True)

# -----------------------------------------------------------
# Backend status
# -----------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_backend_status():
    try:
        resp = requests.get("http://127.0.0.1:8000/home", timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"status": "error", "message": "Backend /home not OK"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

backend_status = get_backend_status()

# -----------------------------------------------------------
# Sidebar – document upload & embedding
# -----------------------------------------------------------
with st.sidebar:
    st.header("📄 Upload & Embed Documents")

    # Backend status in sidebar
    if backend_status.get("status") == "ok":
        st.success("Backend: Ready", icon="✅")
        st.caption(
            f"**{backend_status.get('embedding', '-') }**  \n"
            f"**{backend_status.get('vectorstore', '-') }**  \n"
            f"**{backend_status.get('llm', '-') }**"
        )
    else:
        st.error(f"Backend Error: {backend_status.get('message')}", icon="🚨")

    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} file(s) to `{UPLOAD_DIR}`")

# -----------------------------------------------------------
# Main layout – ChatGPT-like interface with right column
# -----------------------------------------------------------
st.title("💬 RAG Chatbot")

st.caption(
    "Chat with your documents using a ChatGPT-style interface. "
    "Upload and embed files from the sidebar to enhance retrieval."
)

# Layout: main chat (left) and embedded files (right)
left_col, right_col = st.columns([4, 1], gap="large")

# -------------------- LEFT: CHAT ---------------------------
with left_col:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history (no scroll box, just grows downwards)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# -------------------- RIGHT: EMBEDDING PANEL ---------------
with right_col:
    embed_clicked = st.button("🚀 Embed New Documents", use_container_width=True)
    if embed_clicked:
        with st.spinner("Calling backend to embed all documents..."):
            try:
                response = requests.post("http://127.0.0.1:8000/embed_all", timeout=60)
                if response.status_code == 200:
                    # Move all uploaded files to embedded folder
                    for filename in os.listdir(UPLOAD_DIR):
                        src = os.path.join(UPLOAD_DIR, filename)
                        dst = os.path.join(EMBEDDED_DIR, filename)
                        if os.path.isfile(src):
                            shutil.move(src, dst)
                    st.success("Embedding complete. Files moved to embedded folder.")
                else:
                    st.error(f"Embedding failed: {response.text}")
            except Exception as e:
                st.error(f"Embedding failed: {e}")

    st.markdown("---")
    st.subheader("📚 Embedded Files")
    embedded_files = os.listdir(EMBEDDED_DIR)
    if embedded_files:
        for f_name in embedded_files:
            st.markdown(f"- {f_name}")
    else:
        st.info("No embedded files yet.")

# -------------------- BOTTOM: CHAT INPUT -------------------
# (placed AFTER columns so it stays visually at the bottom)
if backend_status.get("status") != "ok":
    st.warning("Backend is not ready. Fix the backend and reload the page to chat.")
    user_input = None
else:
    user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call backend and get response
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input},
            timeout=120,
        )
        if response.status_code == 200:
            bot_reply = response.json().get("response", "No response from backend.")
        else:
            bot_reply = f"Backend error: {response.status_code} - {response.text}"
    except Exception as e:
        bot_reply = f"Error calling backend: {e}"

    # Save bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Rerun so the new messages render in the chat area above
    st.rerun()
