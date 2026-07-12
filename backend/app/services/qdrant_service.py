from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
)
from app.config import settings


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection = settings.QDRANT_COLLECTION
        self.vector_size = settings.VECTOR_SIZE
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            from qdrant_client.models import PayloadSchemaType
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="paper_id",
                field_schema=PayloadSchemaType.INTEGER,
            )

    def upsert_points(
        self,
        points: List[PointStruct],
    ) -> None:
        self.client.upsert(
            collection_name=self.collection,
            points=points,
        )

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        paper_id: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> List[dict]:
        search_filter = None
        if paper_id is not None:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="paper_id",
                        match=MatchValue(value=paper_id),
                    )
                ]
            )

        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            search_params=SearchParams(hnsw_ef=128),
            score_threshold=score_threshold,
        )

        return [
            {
                "paper_id": hit.payload.get("paper_id"),
                "paper_title": hit.payload.get("paper_title", ""),
                "chunk_text": hit.payload.get("chunk_text", ""),
                "chunk_index": hit.payload.get("chunk_index"),
                "score": hit.score,
            }
            for hit in results
        ]

    def delete_paper_points(self, paper_id: int) -> None:
        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="paper_id",
                        match=MatchValue(value=paper_id),
                    )
                ]
            ),
        )

    def get_collection_info(self) -> dict:
        info = self.client.get_collection(collection_name=self.collection)
        return {
            "name": self.collection,
            "vectors_count": info.points_count,
            "status": info.status,
        }


qdrant_service = QdrantService()
