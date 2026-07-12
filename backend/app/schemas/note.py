from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NoteCreate(BaseModel):
    content: str


class NoteUpdate(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: int
    user_id: int
    paper_id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
