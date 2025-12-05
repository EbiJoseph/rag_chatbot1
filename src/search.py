import os
from datetime import datetime
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from src.data_loader import load_all_documents
from langchain_aws import ChatBedrock
import boto3  # if you need it elsewhere; not strictly required here

load_dotenv()


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "amazon.titan-embed-text-v2:0",
        llm_model: str = "amazon.nova-micro-v1:0",
    ):
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
            model_id=llm_model,
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        print(f"[INFO] Amazon Bedrock LLM initialized: {llm_model}")

        # ---------------- Chat history setup ----------------
        chathistory_dir = "chathistory"
        os.makedirs(chathistory_dir, exist_ok=True)

        # One session file per RAGSearch instance, named with start date/time
        session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_file = os.path.join(chathistory_dir, f"session_{session_timestamp}.txt")
        print(f"[INFO] Chat history file: {self.session_file}")

    def _format_context_with_sources(self, results):
        """
        Build a context string that includes the text plus source filename + page number,
        so the model can see which chunk came from where.
        """
        context_chunks = []
        for r in results:
            meta = r.get("metadata", {}) or {}
            text = meta.get("text", "")

            # Try common metadata keys for file and page
            file_name = meta.get("source") or meta.get("file_name") or meta.get("filename") or "Unknown file"
            page = meta.get("page") or meta.get("page_number") or meta.get("page_no")

            if page is not None:
                header = f"[Source: {file_name}, p.{page}]"
            else:
                header = f"[Source: {file_name}]"

            # Combine header + text
            chunk = f"{header}\n{text}"
            context_chunks.append(chunk)

        context = "\n\n".join(context_chunks)
        return context

    def _format_sources_list(self, results):
        """
        Build a nice human-readable list of sources with page numbers for the
        'Sources:' section in the final answer if you ever want to post-process.
        (Not strictly required for the model, but handy if you want to attach later.)
        """
        seen = set()
        sources = []
        for r in results:
            meta = r.get("metadata", {}) or {}
            file_name = meta.get("source") or meta.get("file_name") or meta.get("filename") or "Unknown file"
            page = meta.get("page") or meta.get("page_number") or meta.get("page_no")
            if page is not None:
                key = (file_name, page)
                label = f"{file_name}, p.{page}"
            else:
                key = (file_name, None)
                label = f"{file_name}"

            if key not in seen:
                seen.add(key)
                sources.append(label)

        return sources

    def _append_to_history(self, query: str, answer: str):
        """
        Append the latest user query and assistant answer to the session history file.
        """
        try:
            with open(self.session_file, "a", encoding="utf-8") as f:
                f.write(f"USER: {query}\n")
                f.write(f"ASSISTANT: {answer}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to write chat history: {e}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        # Always reload index from disk before querying
        try:
            self.vectorstore.load()
        except Exception as e:
            print(f"[ERROR] Could not load FAISS index: {e}")

        results = self.vectorstore.query(query, top_k=top_k)

        if not results:
            answer = "No relevant documents found."
            self._append_to_history(query, answer)
            return answer

        # Build context including source + page
        context = self._format_context_with_sources(results)

        if not context.strip():
            answer = "No relevant documents found."
            self._append_to_history(query, answer)
            return answer

        prompt = f"""SYSTEM:
You are a Retrieval-Augmented Q&A assistant. You must answer using ONLY the provided context.
If and only if the answer is clearly present in the context, you should answer the question.

If the answer is NOT present in the context, you MUST:
- Explicitly say you cannot find the answer in the provided documents.
- Set the sources list to contain exactly one entry: "none".

OUTPUT FORMAT (VERY IMPORTANT):
First, write the answer.
Then, on a new line, write the sources in this exact format:

**Sources:**
- none           (if the answer is not in the context)
OR
- filename_1.ext, p.X
- filename_2.ext, p.Y   (only for documents that actually support your answer)

You MUST NOT list any file in **Sources** if it did not directly support your answer.

USER QUERY:
{query}

RETRIEVED CONTEXT:
{context}

TASK:
Answer the user's question using ONLY the retrieved context.
Write a clear, concise answer following the rules above.
"""


        response = self.llm.invoke(prompt)
        answer_text = response.content if hasattr(response, "content") else str(response)

        # Save to chat history
        self._append_to_history(query, answer_text)

        return answer_text


# Example usage
# if __name__ == "__main__":
#     rag_search = RAGSearch()
#     query = "What is official notice period?"
#     summary = rag_search.search_and_summarize(query, top_k=3)
#     print("Summary:", summary)
