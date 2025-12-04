from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import boto3
import json
from src.data_loader import load_all_documents

class EmbeddingPipeline:
    def __init__(self, model_id: str = "amazon.titan-embed-text-v1", chunk_size: int = 1000, chunk_overlap: int = 200, region_name: str = "us-east-1"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_id = model_id
        self.region_name = region_name
        self.bedrock = boto3.client("bedrock-runtime", region_name=self.region_name)
        print(f"[INFO] Using Amazon Bedrock embedding model: {model_id}")

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

    def embed_chunks(self, chunks: List[Any]) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks using Amazon Bedrock...")
        embeddings = []
        for text in texts:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({"inputText": text}).encode("utf-8")
            )
            response_body = json.loads(response["body"].read())
            embed = np.array(response_body["embedding"])
            embeddings.append(embed)
        embeddings = np.stack(embeddings)
        print(f"[INFO] Embeddings shape: {embeddings.shape}")
        return embeddings

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    emb_pipe = EmbeddingPipeline()
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print("[INFO] Example embedding:", embeddings[0] if len(embeddings) > 0 else None)
