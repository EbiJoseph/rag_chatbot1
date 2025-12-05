# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot with a modern React frontend and FastAPI backend, supporting document upload, embedding, semantic search, and chat with source citations.

## Features

- **Document Upload & Embedding:** Upload PDF, DOCX, TXT, CSV, Excel, and JSON files for semantic search.
- **Vector Search:** Uses FAISS for fast similarity search over embedded document chunks.
- **Chatbot:** Ask questions and get answers with cited sources from your documents.
- **Source Attribution:** Each answer includes file name and page number for traceability.
- **Chat History:** All chat sessions are saved as text files in the `chathistory/` folder.
- **Modern UI:** React frontend for chat, file management, and embedded file listing.
- **Amazon Bedrock Integration:** Uses Bedrock for embeddings and LLM responses.

## Folder Structure

```
.
├── agenticrag/                # Experimental/agentic notebooks
├── api.py                     # FastAPI backend entrypoint
├── app.py                     # (Legacy/alt) Streamlit app
├── books.jsonl                # Example data
├── chathistory/               # Saved chat histories (per session)
├── data/
│   ├── embedded/              # Embedded documents (moved after embedding)
│   └── uploaded/              # Uploaded documents (to be embedded)
├── faiss_store/               # FAISS index and metadata
├── frontend/                  # React frontend app
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── Chat.js
│       ├── EmbeddedFiles.js
│       ├── Sidebar.js
│       └── index.js
├── notebook/                  # Jupyter notebooks and sample docs
├── requirements.txt           # Python dependencies
├── src/                       # Core backend logic
│   ├── data_loader.py         # Loads and chunks documents, adds metadata
│   ├── embedding.py           # Embedding pipeline (Bedrock)
│   ├── search.py              # RAG search and summarization logic
│   └── vectorstore.py         # FAISS vector store management
└── typesense.ipynb            # (Optional) Typesense notebook
```

## Setup

### 1. Backend (FastAPI)

1. **Install Python dependencies:**
	```sh
	pip install -r requirements.txt
	```

2. **Set up AWS credentials** for Amazon Bedrock (see AWS documentation).

3. **Run the FastAPI server:**
	```sh
	uvicorn api:app --reload
	```

### 2. Frontend (React)

1. **Install Node dependencies:**
	```sh
	cd frontend
	npm install
	```

2. **Start the React app:**
	```sh
	npm start
	```

3. The app will be available at [http://localhost:3000](http://localhost:3000).

### 3. Usage

- Upload documents via the frontend.
- Click "Embed All" to process and index new documents.
- Ask questions in the chat; answers will cite sources (file and page).
- View embedded files and chat history.

## Key Files

- `api.py`: FastAPI backend, exposes endpoints for chat, embedding, file upload, and health checks.
- `src/data_loader.py`: Loads documents and ensures each chunk has `source` (filename) and `page` metadata.
- `src/vectorstore.py`: Handles FAISS index creation, saving, loading, and querying.
- `frontend/src/`: React components for chat, file upload, and embedded file management.

## Notes

- All chat history is saved in `chathistory/` as timestamped `.txt` files.
- Embedded documents are moved from `data/uploaded/` to `data/embedded/` after processing.
- The backend must be running for the frontend to function.
- Ensure CORS is enabled in FastAPI for frontend-backend communication.

## License

See `LICENSE` file.
