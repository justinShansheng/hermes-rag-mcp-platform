import os
from typing import List

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


class RAGService:
    def __init__(self):
        self.embedding_model = "nomic-embed-text"
        self.embeddings = OllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=self.embedding_model,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
        )
        self.vectorstore = None

    async def index_files(self, files: List[str]) -> dict:
        documents: List[Document] = []

        for p in files:
            path = os.path.abspath(p)
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                continue

            chunks = self.splitter.split_text(content)
            for chunk in chunks:
                documents.append(Document(page_content=chunk, metadata={"source": path}))

        if not documents:
            return {"indexed": 0, "status": "no_documents"}

        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        return {"indexed": len(documents), "status": "ok"}

    async def search(self, query: str, top_k: int = 5) -> list:
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search(query, k=top_k)
        return [
            {
                "content": item.page_content,
                "source": item.metadata.get("source", "unknown"),
            }
            for item in results
        ]

    async def answer_with_context(self, question: str, context: List[dict], model: str = None, llm_service=None) -> str:
        if not context:
            return "I do not yet have enough grounded knowledge to answer this question. Add documents or connect an MCP tool."

        context_text = "\n\n".join(item["content"] for item in context)
        prompt = f"""
You are Hermes Agent.
Use the context below to answer as accurately as possible.
Do not invent facts.

Context:
{context_text}

User question:
{question}
"""

        if llm_service is not None and model:
            try:
                return await llm_service.generate(model=model, prompt=prompt)
            except Exception:
                pass

        return prompt
