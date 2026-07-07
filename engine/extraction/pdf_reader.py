from __future__ import annotations

from pathlib import Path
from typing import List

import pdfplumber
from PyPDF2 import PdfReader


def read_pdf_text(path: Path) -> str:
    parts: List[str] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text:
                    parts.append(text)
    except Exception:
        parts = []

    text = "\n".join(parts).strip()
    if text:
        return text

    try:
        reader = PdfReader(str(path))
        chunks = []
        for page in reader.pages:
            try:
                chunk = page.extract_text() or ""
            except Exception:
                chunk = ""
            if chunk:
                chunks.append(chunk)
        return "\n".join(chunks).strip()
    except Exception:
        return ""
