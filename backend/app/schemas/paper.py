from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PaperCreate(BaseModel):
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None


class PaperResponse(BaseModel):
    id: int
    title: str
    authors: Optional[str]
    abstract: Optional[str]
    file_path: Optional[str]
    uploaded_at: datetime
    uploaded_by: int

    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    id: int
    title: str
    authors: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    paper_id: int
    summary: str


class RelatedPaperResponse(BaseModel):
    id: int
    title: str
    authors: Optional[str]
    similarity_score: float
