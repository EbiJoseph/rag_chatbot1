from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import os, shutil
from src.data_loader import load_all_documents
from langchain_aws import BedrockEmbeddings
from tqdm import tqdm
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class EmbeddingPipeline:
    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0", chunk_size: int = 1000, chunk_overlap: int = 200, region_name: str = "us-east-1"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_id = model_id
        self.region_name = region_name
        self.embedder = BedrockEmbeddings(model_id=self.model_id, region_name=self.region_name)
        print(f"[INFO] Using LangChain BedrockEmbeddings model: {model_id}")

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def embed_chunks(self, chunks: List[Any], move_files: bool = True, uploaded_dir: str = "data/uploaded", embedded_dir: str = "data/embedded", batch_size: int = 32) -> np.ndarray:
        
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks using LangChain BedrockEmbeddings (batch size={batch_size})...")
        if len(texts) == 0:
            print("[INFO] No chunks to embed. Returning empty array.")
            return np.array([])
        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
            batch = texts[i:i+batch_size]
            batch_embeds = self.embedder.embed_documents(batch)
            embeddings.extend(batch_embeds)
        embeddings = np.stack(embeddings)
        print(f"[INFO] Embeddings shape: {embeddings.shape}")
        if move_files:
            self.move_uploaded_to_embedded(uploaded_dir, embedded_dir)
        return embeddings
    def move_uploaded_to_embedded(self, uploaded_dir: str = "data/uploaded", embedded_dir: str = "data/embedded"):
        os.makedirs(embedded_dir, exist_ok=True)
        for filename in os.listdir(uploaded_dir):
            src = os.path.join(uploaded_dir, filename)
            dst = os.path.join(embedded_dir, filename)
            if os.path.isfile(src):
                shutil.move(src, dst)
        print(f"[INFO] Moved files from {uploaded_dir} to {embedded_dir}")

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data/uploaded")
    emb_pipe = EmbeddingPipeline()
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print("[INFO] Example embedding:", embeddings[0] if len(embeddings) > 0 else None)
