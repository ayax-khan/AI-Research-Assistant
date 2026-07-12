from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from app.services.llm_service import llm_service
from app.services.qdrant_service import qdrant_service
from app.utils.prompt_templates import PromptTemplates


class QAState(TypedDict):
    query: str
    paper_id: Optional[int]
    query_vector: List[float]
    retrieved_chunks: List[dict]
    context: str
    answer: str
    error: str | None


async def embed_question(state: QAState) -> QAState:
    try:
        query_vector = await llm_service.get_embedding(state["query"])
        return {**state, "query_vector": query_vector, "error": None}
    except Exception as e:
        return {**state, "error": str(e)}


async def retrieve_chunks(state: QAState) -> QAState:
    try:
        results = qdrant_service.search(
            query_vector=state["query_vector"],
            top_k=5,
            paper_id=state.get("paper_id"),
        )
        return {**state, "retrieved_chunks": results}
    except Exception as e:
        return {**state, "error": str(e)}


async def format_prompt(state: QAState) -> QAState:
    try:
        if not state["retrieved_chunks"]:
            return {**state, "context": "", "error": "No relevant documents found"}

        context_parts = []
        for r in state["retrieved_chunks"]:
            title = r.get("paper_title", "Unknown")
            text = r.get("chunk_text", "")
            context_parts.append(f"[{title}]: {text}")

        context = "\n\n".join(context_parts)
        return {**state, "context": context}
    except Exception as e:
        return {**state, "error": str(e)}


async def generate_answer(state: QAState) -> QAState:
    try:
        if not state["context"]:
            return {
                **state,
                "answer": "No relevant information found to answer your question.",
            }

        prompt = PromptTemplates.qa_prompt(
            context=state["context"],
            question=state["query"],
        )
        answer = await llm_service.generate_text(prompt, temperature=0.3)
        return {**state, "answer": answer}
    except Exception as e:
        return {**state, "error": str(e)}


def create_qa_graph() -> StateGraph:
    workflow = StateGraph(QAState)

    workflow.add_node("embed_question", embed_question)
    workflow.add_node("retrieve_chunks", retrieve_chunks)
    workflow.add_node("format_prompt", format_prompt)
    workflow.add_node("generate_answer", generate_answer)

    workflow.set_entry_point("embed_question")
    workflow.add_edge("embed_question", "retrieve_chunks")
    workflow.add_edge("retrieve_chunks", "format_prompt")
    workflow.add_edge("format_prompt", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()


qa_graph = create_qa_graph()
