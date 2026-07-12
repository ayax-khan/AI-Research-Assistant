import pytest
from app.services.chunker import TextChunker


class TestTextChunker:
    def test_semantic_chunk_simple(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = TextChunker.semantic_chunk(text, max_chunk_size=500)
        assert len(chunks) == 3
        assert "First paragraph." in chunks[0]

    def test_semantic_chunk_large(self):
        text = "A" * 300 + "\n\n" + "B" * 300 + "\n\n" + "C" * 300
        chunks = TextChunker.semantic_chunk(text, max_chunk_size=400)
        assert len(chunks) >= 2

    def test_chunk_text_empty(self):
        chunks = TextChunker.chunk_text("", chunk_size=100, chunk_overlap=20)
        assert chunks == []

    def test_chunk_text_single(self):
        chunks = TextChunker.chunk_text("Hello world", chunk_size=100, chunk_overlap=20)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"
