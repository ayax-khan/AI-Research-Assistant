import fitz
from pathlib import Path
from typing import Optional


class PDFProcessor:
    @staticmethod
    def extract_text(pdf_path: str | Path) -> str:
        doc = fitz.open(str(pdf_path))
        full_text = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                full_text.append(text)
        doc.close()
        return "\n\n".join(full_text)

    @staticmethod
    def extract_metadata(pdf_path: str | Path) -> dict:
        doc = fitz.open(str(pdf_path))
        metadata = doc.metadata or {}
        doc.close()
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
        }
