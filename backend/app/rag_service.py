import os
from typing import List

from langchain_core.documents import Document

from app.config import settings
from app.vector_store import VectorStore


class RAGService:
    def __init__(self):
        self.vector_store = VectorStore(base_url=settings.ollama_base_url)

    async def index_files(self, files: List[str]) -> dict:
        documents: list[Document] = []
        for path in files:
            file_path = os.path.abspath(path)
            if not os.path.exists(file_path):
                continue
            documents.extend(self.vector_store.chunks_from_file(file_path))

        if not documents:
            return {"indexed": 0, "status": "no_documents"}

        count = self.vector_store.index_documents(documents)
        return {"indexed": count, "status": "ok"}

    async def search(self, query: str, top_k: int = 5) -> list:
        return self.vector_store.search(query=query, top_k=top_k)

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
