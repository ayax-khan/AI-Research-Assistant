from fastapi import APIRouter, Depends
from typing import List
from app.models.user import User
from app.schemas.search import QueryRequest, QueryResponse, SearchRequest, SearchResult
from app.core.deps import get_current_user
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.qdrant_service import qdrant_service

router = APIRouter(prefix="/api", tags=["Search & Query"])


@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    return await rag_service.answer_question(
        query=payload.query,
        paper_id=payload.paper_id,
        top_k=payload.k,
    )


@router.post("/search", response_model=List[SearchResult])
async def search_papers(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    query_vector = await llm_service.get_embedding(payload.query)
    results = qdrant_service.search(
        query_vector=query_vector,
        top_k=payload.k,
        paper_id=payload.paper_id,
    )
    return [
        SearchResult(
            paper_id=r["paper_id"],
            paper_title=r["paper_title"],
            chunk_text=r["chunk_text"],
            score=r["score"],
        )
        for r in results
    ]
