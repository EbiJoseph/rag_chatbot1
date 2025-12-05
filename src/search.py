
import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from src.data_loader import load_all_documents
from langchain_aws import ChatBedrock
import boto3

load_dotenv()


class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "amazon.titan-embed-text-v2:0", llm_model: str = "amazon.nova-micro-v1:0"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            docs = load_all_documents("data/uploaded")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()

        # Set up Bedrock client (credentials should be set in environment or AWS config)
        self.llm = ChatBedrock(
            model_id=llm_model,  # e.g., "anthropic.claude-v2:1" or another valid Bedrock chat model version
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        print(f"[INFO] Amazon Bedrock LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        # Always reload index from disk before querying
        try:
            self.vectorstore.load()
        except Exception as e:
            print(f"[ERROR] Could not load FAISS index: {e}")
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        prompt = f"""You're chatbot agent give answer with short explanation: '{query}'\n\nContext:\n{context}\n\nAnswer:"""
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else response

# Example usage
# if __name__ == "__main__":
#     rag_search = RAGSearch()
#     query = "What is offical notice period?"
#     summary = rag_search.search_and_summarize(query, top_k=3)
#     print("Summary:", summary)
