from __future__ import annotations

from typing import List, Dict


def rank_vendors(profiles: List[Dict]) -> List[Dict]:
    ranked = []
    for profile in profiles:
        commercial = profile.get("commercial", {})
        score = 0
        for field in ["price", "delivery", "warranty", "payment_terms", "taxes", "emd", "net_worth", "annual_turnover"]:
            if commercial.get(field):
                score += 1
        ranked.append({
            "vendor": profile.get("vendor"),
            "score": score,
            "confidence": profile.get("confidence"),
            "file_name": profile.get("file_name"),
        })
    return sorted(ranked, key=lambda item: (-item["score"], item["vendor"]))
