import os
from typing import Any, List

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class VectorStore:
    def __init__(self, base_url: str, collection_name: str = "hermes_docs"):
        self.collection_name = collection_name
        self.embeddings = OllamaEmbeddings(base_url=base_url, model="nomic-embed-text")
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
        self.vectorstore = None

    def index_documents(self, documents: List[Document]) -> int:
        if not documents:
            return 0
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        return len(documents)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
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

    def chunks_from_file(self, file_path: str) -> List[Document]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        chunks = self.splitter.split_text(content)
        return [Document(page_content=chunk, metadata={"source": file_path}) for chunk in chunks]


class LocalVectorStore(VectorStore):
    def __init__(self, base_url: str, storage_dir: str = "./data/faiss"):
        super().__init__(base_url=base_url)
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def persist(self, name: str = "default") -> str:
        if self.vectorstore is None:
            raise ValueError("No vector store available to persist")
        target = os.path.join(self.storage_dir, name)
        self.vectorstore.save_local(target)
        return target

    def load(self, name: str = "default") -> None:
        target = os.path.join(self.storage_dir, name)
        if not os.path.exists(target):
            return
        self.vectorstore = FAISS.load_local(target, self.embeddings, allow_dangerous_deserialization=True)
