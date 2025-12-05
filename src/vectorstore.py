import os
import faiss
import numpy as np
import pickle
from typing import List, Any
import boto3
from src.embedding import EmbeddingPipeline
import json

class FaissVectorStore: 
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "amazon.titan-embed-text-v2:0", chunk_size: int = 1000, chunk_overlap: int = 200, region_name: str = "us-east-1",llm_model: str = "amazon.nova-micro-v1:0"):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.metadata = []
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.region_name = region_name
        self.bedrock = boto3.client("bedrock-runtime", region_name=self.region_name)
        print(f"[INFO] Using Amazon Bedrock embedding model: {embedding_model}")

    def build_from_documents(self, documents: List[Any]):
        if not documents or len(documents) == 0:
            print("[INFO] No documents provided. Skipping FAISS store build.")
            return
        print(f"[INFO] Building vector store from {len(documents)} raw documents...")
        emb_pipe = EmbeddingPipeline(model_id=self.embedding_model, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, region_name=self.region_name)
        chunks = emb_pipe.chunk_documents(documents)
        if not chunks or len(chunks) == 0:
            print("[INFO] No chunks generated from documents. Skipping FAISS store build.")
            return
        embeddings = emb_pipe.embed_chunks(chunks)
        if embeddings is None or len(embeddings) == 0:
            print("[INFO] No embeddings generated. Skipping FAISS store build.")
            return
        metadatas = [{"text": chunk.page_content} for chunk in chunks]
        self.add_embeddings(np.array(embeddings).astype('float32'), metadatas)
        self.save()
        print(f"[INFO] Vector store built and saved to {self.persist_dir}")

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None):
        if embeddings is None or len(embeddings) == 0 or (hasattr(embeddings, 'shape') and embeddings.shape[0] == 0):
            print("[INFO] No embeddings to add. Skipping.")
            return
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadatas:
            self.metadata.extend(metadatas)
        print(f"[INFO] Added {embeddings.shape[0]} vectors to Faiss index.")

    def save(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        faiss.write_index(self.index, faiss_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[INFO] Saved Faiss index and metadata to {self.persist_dir}")

    def load(self, documents: List[Any] = None):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            print(f"[INFO] Faiss index not found. Building new index...")
            if documents is None:
                raise FileNotFoundError("No index found and no documents provided to build one.")
            self.build_from_documents(documents)
        self.index = faiss.read_index(faiss_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[INFO] Loaded Faiss index and metadata from {self.persist_dir}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        if self.index is None:
            print("[INFO] No FAISS index available. Returning empty search results.")
            return []
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            meta = self.metadata[idx] if idx < len(self.metadata) else None
            results.append({"index": idx, "distance": dist, "metadata": meta})
        return results

    def query(self, query_text: str, top_k: int = 5):
        print(f"[INFO] Querying vector store for: '{query_text}'")
        if self.index is None:
            print("[INFO] No FAISS index available. Returning empty query results.")
            return []
        # Use Bedrock to embed the query text
        response = self.bedrock.invoke_model(
            modelId=self.embedding_model,
            body=json.dumps({"inputText": query_text}).encode("utf-8")
        )
        response_body = json.loads(response["body"].read())
        query_emb = np.array(response_body["embedding"]).reshape(1, -1).astype('float32')
        return self.search(query_emb, top_k=top_k)

# Example usage
# if __name__ == "__main__":
#     from data_loader import load_all_documents
#     docs = load_all_documents("data")
#     store = FaissVectorStore("faiss_store")
#     store.load(documents=docs)
#     print(store.query("What is offical notice period?", top_k=3))
