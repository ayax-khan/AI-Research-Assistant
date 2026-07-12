from typing import List
from app.config import settings


class TextChunker:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        separators = ["\n\n", "\n", ". ", " ", ""]
        chunks = []
        current = ""
        for paragraph in text.split("\n\n"):
            if len(current) + len(paragraph) < chunk_size:
                current += ("\n\n" + paragraph) if current else paragraph
            else:
                if current:
                    chunks.append(current.strip())
                current = paragraph

                while len(current) > chunk_size:
                    chunks.append(current[:chunk_size].strip())
                    current = current[chunk_size - chunk_overlap:]

        if current:
            chunks.append(current.strip())

        return chunks

    @staticmethod
    def semantic_chunk(text: str, max_chunk_size: int = None) -> List[str]:
        max_chunk_size = max_chunk_size or settings.CHUNK_SIZE
        sections = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for section in sections:
            if len(current_chunk) + len(section) < max_chunk_size:
                current_chunk += ("\n\n" + section) if current_chunk else section
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
