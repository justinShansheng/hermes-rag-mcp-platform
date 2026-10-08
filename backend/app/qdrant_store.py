from typing import Any, List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings


class QdrantVectorStore:
    def __init__(self, url: str, collection_name: str = "hermes_docs"):
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self._init_collection()

    def _init_collection(self) -> None:
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def add_documents(self, documents: List[dict[str, Any]]) -> List[str]:
        points = []
        ids = []
        for i, doc in enumerate(documents):
            point_id = i + 1
            ids.append(str(point_id))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=doc["vector"],
                    payload={
                        "content": doc["content"],
                        "source": doc.get("source", "unknown"),
                        "metadata": doc.get("metadata", {}),
                    },
                )
            )
        self.client.upsert(collection_name=self.collection_name, points=points)
        return ids

    def search(self, query_vector: List[float], top_k: int = 5) -> list[dict[str, Any]]:
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "content": result.payload.get("content", ""),
                "source": result.payload.get("source", "unknown"),
            }
            for result in results
        ]
