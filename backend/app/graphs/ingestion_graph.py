from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from app.services.pdf_processor import PDFProcessor
from app.services.chunker import TextChunker
from app.services.llm_service import llm_service
from app.services.qdrant_service import qdrant_service
from qdrant_client.models import PointStruct
import uuid


class IngestionState(TypedDict):
    pdf_path: str
    paper_id: int
    paper_title: str
    raw_text: str
    chunks: List[str]
    vectors: List[list]
    points: List[PointStruct]
    error: str | None


async def extract_text(state: IngestionState) -> IngestionState:
    try:
        raw_text = PDFProcessor.extract_text(state["pdf_path"])
        return {**state, "raw_text": raw_text, "error": None}
    except Exception as e:
        return {**state, "error": str(e)}


async def chunk_text(state: IngestionState) -> IngestionState:
    try:
        chunks = TextChunker.semantic_chunk(state["raw_text"])
        return {**state, "chunks": chunks}
    except Exception as e:
        return {**state, "error": str(e)}


async def embed_chunks(state: IngestionState) -> IngestionState:
    try:
        vectors = []
        for chunk in state["chunks"]:
            vector = await llm_service.get_embedding(chunk)
            vectors.append(vector)
        return {**state, "vectors": vectors}
    except Exception as e:
        return {**state, "error": str(e)}


async def store_vectors(state: IngestionState) -> IngestionState:
    try:
        points = []
        for i, (chunk, vector) in enumerate(zip(state["chunks"], state["vectors"])):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "paper_id": state["paper_id"],
                        "paper_title": state["paper_title"],
                        "chunk_index": i,
                        "chunk_text": chunk,
                    },
                )
            )
        qdrant_service.upsert_points(points)
        return {**state, "points": points}
    except Exception as e:
        return {**state, "error": str(e)}


def create_ingestion_graph() -> StateGraph:
    workflow = StateGraph(IngestionState)

    workflow.add_node("extract_text", extract_text)
    workflow.add_node("chunk_text", chunk_text)
    workflow.add_node("embed_chunks", embed_chunks)
    workflow.add_node("store_vectors", store_vectors)

    workflow.set_entry_point("extract_text")
    workflow.add_edge("extract_text", "chunk_text")
    workflow.add_edge("chunk_text", "embed_chunks")
    workflow.add_edge("embed_chunks", "store_vectors")
    workflow.add_edge("store_vectors", END)

    return workflow.compile()


ingestion_graph = create_ingestion_graph()
