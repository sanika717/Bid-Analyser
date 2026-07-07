from __future__ import annotations

from typing import Dict

from sentence_transformers import SentenceTransformer

_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def extract_unstructured_values(text: str) -> Dict[str, str]:
    sections = [chunk.strip() for chunk in text.splitlines() if chunk.strip()]
    if not sections:
        return {}
    embeddings = _MODEL.encode(sections, convert_to_numpy=True)
    _ = embeddings
    return {
        "summary": sections[0][:200],
        "evidence": " | ".join(sections[:3]),
    }
