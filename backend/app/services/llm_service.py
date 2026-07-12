from typing import Optional, List
from openai import AsyncOpenAI
import google.generativeai as genai
import asyncio
from app.config import settings


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self._openai_client: Optional[AsyncOpenAI] = None
        self._genai_configured = False

    def _get_openai(self) -> AsyncOpenAI:
        if self._openai_client is None:
            self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client

    def _ensure_genai(self):
        if not self._genai_configured and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._genai_configured = True

    async def get_embedding(self, text: str) -> List[float]:
        if self.provider == "gemini":
            return await asyncio.to_thread(self._get_gemini_embedding_sync, text)
        return await self._get_openai_embedding(text)

    async def _get_openai_embedding(self, text: str) -> List[float]:
        client = self._get_openai()
        response = await client.embeddings.create(
            input=text,
            model=settings.OPENAI_EMBEDDING_MODEL,
        )
        return response.data[0].embedding

    def _get_gemini_embedding_sync(self, text: str) -> List[float]:
        self._ensure_genai()
        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    async def generate_text(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = 1024,
    ) -> str:
        if self.provider == "gemini":
            return await asyncio.to_thread(
                self._generate_gemini_sync, prompt, temperature, max_tokens
            )
        return await self._generate_openai(prompt, temperature, max_tokens)

    async def _generate_openai(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = 1024,
    ) -> str:
        client = self._get_openai()
        response = await client.chat.completions.create(
            model=settings.OPENAI_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature or settings.TEMPERATURE,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _generate_gemini_sync(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = 1024,
    ) -> str:
        self._ensure_genai()
        model = genai.GenerativeModel(settings.GEMINI_LLM_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()


llm_service = LLMService()
