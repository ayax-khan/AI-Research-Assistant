from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str
    k: int = 5
    paper_id: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]


class SearchRequest(BaseModel):
    query: str
    k: int = 10
    paper_id: Optional[int] = None


class SearchResult(BaseModel):
    paper_id: int
    paper_title: str
    chunk_text: str
    score: float
