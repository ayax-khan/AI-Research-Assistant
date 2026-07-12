from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.note import Note
from app.models.paper import Paper
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/api", tags=["Notes"])


@router.get("/papers/{paper_id}/notes", response_model=List[NoteResponse])
async def list_notes(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note).where(
            Note.paper_id == paper_id,
            Note.user_id == current_user.id,
        ).order_by(Note.created_at.desc())
    )
    return result.scalars().all()


@router.post("/papers/{paper_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    paper_id: int,
    payload: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = await db.execute(select(Paper).where(Paper.id == paper_id))
    if not paper.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paper not found")

    note = Note(
        user_id=current_user.id,
        paper_id=paper_id,
        content=payload.content,
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    note.content = payload.content
    await db.flush()
    await db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(note)
