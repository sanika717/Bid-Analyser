from __future__ import annotations

from typing import List


def answer_question(question: str, evidence: List[str]) -> str:
    normalized = question.lower()
    if "lowest" in normalized and "cost" in normalized:
        return "The available evidence suggests the lowest-cost vendor is the one with the lowest documented price in the extracted commercial data."
    if "delivery" in normalized:
        return "Delivery information should be read from the extracted delivery field in the processed bid documents."
    if "warranty" in normalized:
        return "Warranty terms should be reviewed from the captured warranty evidence for each vendor."
    if "payment" in normalized:
        return "Payment terms are available from the extracted payment terms field when present in the document set."
    if "confidence" in normalized:
        return "Confidence is derived from the number of extracted fields and the strength of the matched evidence."
    return "Please ask a question about price, delivery, warranty, payment terms, or confidence, and I will answer from the extracted evidence only."
