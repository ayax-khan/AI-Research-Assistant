from typing import List, Optional
from app.services.llm_service import llm_service
from app.services.qdrant_service import qdrant_service
from app.utils.prompt_templates import PromptTemplates


class RAGService:
    async def answer_question(
        self,
        query: str,
        paper_id: Optional[int] = None,
        top_k: int = 5,
    ) -> dict:
        query_vector = await llm_service.get_embedding(query)

        results = qdrant_service.search(
            query_vector=query_vector,
            top_k=top_k,
            paper_id=paper_id,
        )

        if not results:
            return {
                "answer": "No relevant information found to answer your question.",
                "sources": [],
            }

        context = []
        for r in results:
            context.append(f"[{r['paper_title']}]: {r['chunk_text']}")

        prompt = PromptTemplates.qa_prompt(
            context="\n\n".join(context),
            question=query,
        )

        answer = await llm_service.generate_text(prompt, temperature=0.3)

        sources = [
            {
                "paper_id": r["paper_id"],
                "paper_title": r["paper_title"],
                "excerpt": r["chunk_text"][:200],
                "score": r["score"],
            }
            for r in results[:3]
        ]

        return {"answer": answer, "sources": sources}

    async def summarize_paper(self, paper_text: str, paper_title: str) -> str:
        prompt = PromptTemplates.summarization_prompt(
            paper_text=paper_text,
            paper_title=paper_title,
        )
        return await llm_service.generate_text(prompt, temperature=0.5, max_tokens=500)

    async def find_related_papers(
        self,
        query_vector: List[float],
        exclude_paper_id: int,
        top_k: int = 5,
    ) -> List[dict]:
        results = qdrant_service.search(
            query_vector=query_vector,
            top_k=top_k + 5,
        )
        return [
            r for r in results
            if r["paper_id"] != exclude_paper_id
        ][:top_k]


rag_service = RAGService()
