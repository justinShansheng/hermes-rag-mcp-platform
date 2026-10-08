import os
import logging
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self.dimension = 384
        self._init_index()

    def _init_index(self):
        """Initialize FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)

    def chunks_from_file(self, file_path: str) -> List[Document]:
        """Extract chunks from file"""
        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_text(text)
        return [Document(page_content=chunk, metadata={"source": file_path}) for chunk in chunks]

    def index_documents(self, documents: List[Document]) -> int:
        """Index documents"""
        if not documents:
            return 0

        try:
            embeddings = []
            for doc in documents:
                embedding = self.model.encode(doc.page_content)
                embeddings.append(embedding.astype(np.float32))
                self.documents.append(doc.page_content)

            embeddings_array = np.array(embeddings)
            self.index.add(embeddings_array)
            return len(documents)
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            return 0

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Search for relevant documents"""
        if not self.documents or self.index.ntotal == 0:
            return []

        try:
            query_embedding = self.model.encode(query).astype(np.float32).reshape(1, -1)
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.documents):
                    results.append({"content": self.documents[idx], "score": float(distances[0][list(indices[0]).index(idx)])})
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
