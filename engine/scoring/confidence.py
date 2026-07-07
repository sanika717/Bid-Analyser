from __future__ import annotations

from typing import Dict


def score_profile(values: Dict[str, str]) -> str:
    matched = sum(1 for value in values.values() if value and str(value).strip())
    if matched >= 6:
        return "high"
    if matched >= 3:
        return "medium"
    return "low"
