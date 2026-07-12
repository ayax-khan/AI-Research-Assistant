from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import os
import uuid
from pathlib import Path
from app.database import get_db
from app.models.user import User
from app.models.paper import Paper
from app.schemas.paper import PaperCreate, PaperResponse, PaperListResponse, SummaryResponse, RelatedPaperResponse
from app.schemas.search import QueryRequest, QueryResponse
from app.core.deps import get_current_user
from app.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.chunker import TextChunker
from app.services.llm_service import llm_service
from app.services.qdrant_service import qdrant_service
from app.services.rag_service import rag_service
from app.graphs.ingestion_graph import ingestion_graph

router = APIRouter(prefix="/api/papers", tags=["Papers"])


@router.post("/", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    title: str = Form(...),
    authors: Optional[str] = Form(None),
    abstract: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    saved_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / saved_name

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    with open(file_path, "wb") as f:
        f.write(content)

    paper = Paper(
        title=title,
        authors=authors,
        abstract=abstract,
        file_path=str(file_path),
        uploaded_by=current_user.id,
    )
    db.add(paper)
    await db.flush()
    await db.refresh(paper)

    raw_text = PDFProcessor.extract_text(file_path)
    chunks = TextChunker.semantic_chunk(raw_text)
    vectors = []
    for chunk in chunks:
        vector = await llm_service.get_embedding(chunk)
        vectors.append(vector)

    from qdrant_client.models import PointStruct
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "paper_id": paper.id,
                "paper_title": paper.title,
                "chunk_index": i,
                "chunk_text": chunk,
            },
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    qdrant_service.upsert_points(points)

    return paper


@router.get("/", response_model=List[PaperListResponse])
async def list_papers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Paper).order_by(Paper.uploaded_at.desc())
    )
    papers = result.scalars().all()
    return papers


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/{paper_id}/summary", response_model=SummaryResponse)
async def summarize_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if paper.file_path and Path(paper.file_path).exists():
        raw_text = PDFProcessor.extract_text(paper.file_path)
    else:
        raw_text = paper.abstract or ""

    summary = await rag_service.summarize_paper(raw_text, paper.title)
    return SummaryResponse(paper_id=paper_id, summary=summary)


@router.get("/{paper_id}/related", response_model=List[RelatedPaperResponse])
async def get_related_papers(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if paper.file_path and Path(paper.file_path).exists():
        raw_text = PDFProcessor.extract_text(paper.file_path)
        sample = raw_text[:2000]
    else:
        sample = (paper.abstract or paper.title)

    query_vector = await llm_service.get_embedding(sample)
    related = qdrant_service.search(
        query_vector=query_vector,
        top_k=10,
    )
    related = [r for r in related if r["paper_id"] != paper_id][:5]

    results = []
    for r in related:
        paper_result = await db.execute(select(Paper).where(Paper.id == r["paper_id"]))
        p = paper_result.scalar_one_or_none()
        if p:
            results.append(
                RelatedPaperResponse(
                    id=p.id,
                    title=p.title,
                    authors=p.authors,
                    similarity_score=r["score"],
                )
            )
    return results


@router.post("/{paper_id}/ask", response_model=QueryResponse)
async def ask_paper_question(
    paper_id: int,
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    payload.paper_id = paper_id
    return await rag_service.answer_question(
        query=payload.query,
        paper_id=paper_id,
        top_k=payload.k,
    )


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if paper.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if paper.file_path and Path(paper.file_path).exists():
        Path(paper.file_path).unlink()

    qdrant_service.delete_paper_points(paper_id)
    await db.delete(paper)
