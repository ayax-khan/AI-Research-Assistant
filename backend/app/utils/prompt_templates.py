class PromptTemplates:
    @staticmethod
    def qa_prompt(context: str, question: str) -> str:
        return f"""You are a research assistant. Use the following excerpts from academic papers to answer the question truthfully, citing sources in [Title, Year] format.

Context:
{context}

Question: {question}

Answer:"""

    @staticmethod
    def summarization_prompt(paper_text: str, paper_title: str) -> str:
        return f"""You are an expert academic summarizer. Summarize the following research paper "{paper_title}" in approximately 200 words, focusing on key contributions and findings. Do not hallucinate and cite key points.

Paper Text:
{paper_text[:8000]}

Summary:"""

    @staticmethod
    def simple_qa_prompt(context: str, question: str) -> str:
        return f"""Context: {context}

Task: Answer the query below using ONLY the information given in the context. Provide an answer with bullet points and include in-text citations to the sources.

Query: {question}

Answer:"""
