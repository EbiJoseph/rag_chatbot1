from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import os
import shutil
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.search import RAGSearch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


# Initialize RAGSearch (handles loading vectorstore internally)
rag_search = RAGSearch()
UPLOAD_DIR = "data/uploaded"
EMBEDDED_DIR = "data/embedded"
@app.post("/embed_all")
async def embed_all_endpoint():
    docs = load_all_documents(UPLOAD_DIR)
    if not docs:
        return {"status": "no_files", "detail": "No documents to embed."}
    store = FaissVectorStore("faiss_store")
    store.load(documents=docs)
    store.build_from_documents(docs)
    # Move files from uploaded to embedded
    for filename in os.listdir(UPLOAD_DIR):
        src = os.path.join(UPLOAD_DIR, filename)
        dst = os.path.join(EMBEDDED_DIR, filename)
        if os.path.isfile(src):
            shutil.move(src, dst)
    return {"status": "success", "detail": f"Embedded and moved {len(docs)} documents."}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    summary = rag_search.search_and_summarize(user_message, top_k=3)
    return ChatResponse(response=summary)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/home")
async def home_status():
    # Check embedding model
    try:
        embedding_model = rag_search.vectorstore.embedding_model
        embedding_status = f"Embedding model: {embedding_model}"
    except Exception as e:
        embedding_status = f"Embedding model error: {e}"

    # Check vectorstore
    try:
        index_loaded = rag_search.vectorstore.index is not None
        meta_loaded = bool(rag_search.vectorstore.metadata)
        vectorstore_status = f"Vectorstore loaded: {index_loaded and meta_loaded}"
    except Exception as e:
        vectorstore_status = f"Vectorstore error: {e}"

    # Check LLM
    try:
        llm_model = getattr(rag_search.llm, 'model_id', 'unknown')
        llm_status = f"LLM: {llm_model}"
    except Exception as e:
        llm_status = f"LLM error: {e}"

    return {
        "status": "ok",
        "embedding": embedding_status,
        "vectorstore": vectorstore_status,
        "llm": llm_status,
        "message": "Backend is ready for query."
    }

    # Endpoint for file upload (for React frontend)
@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    UPLOAD_DIR = "data/uploaded"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file.filename)
    return {"status": "success", "files": saved_files}

# Endpoint to list embedded files (for React frontend)
@app.get("/embedded_files")
async def list_embedded_files():
    EMBEDDED_DIR = "data/embedded"
    os.makedirs(EMBEDDED_DIR, exist_ok=True)
    files = [f for f in os.listdir(EMBEDDED_DIR) if os.path.isfile(os.path.join(EMBEDDED_DIR, f))]
    return JSONResponse(content={"files": files})