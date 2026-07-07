from __future__ import annotations

from pathlib import Path
from typing import List
from datetime import datetime

from engine.extraction.pdf_reader import read_pdf_text
from engine.extraction.structured import extract_structured_values
from engine.extraction.semi_structured import extract_semi_structured_values
from engine.extraction.unstructured import extract_unstructured_values
from engine.scoring.confidence import score_profile
from engine.scoring.ranking import rank_vendors
from engine.excel.writer import write_workbook


def run_bid_job(pdf_files: List[str], template_file: str) -> dict:
    template_path = Path(template_file)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    profiles = []
    for pdf_path in pdf_files:
        path = Path(pdf_path)
        if not path.exists():
            continue
        text = read_pdf_text(path)
        structured = extract_structured_values(text, str(template_path))
        semi = extract_semi_structured_values(text, str(template_path))
        unstructured = extract_unstructured_values(text)
        merged = {}
        for source in [structured, semi, unstructured]:
            merged.update({k: v for k, v in source.items() if v})
        profile = {
            "vendor": path.stem,
            "file_name": path.name,
            "doc_type": "unstructured" if not structured and not semi else "structured" if structured else "semi_structured",
            "confidence": score_profile(merged),
            "commercial": merged,
        }
        profiles.append(profile)

    ranked = rank_vendors(profiles)
    output_dir = Path(__file__).resolve().parent.parent.parent / "storage" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"TCE_BID_OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    write_workbook(output_file, profiles, ranked)
    return {"output_file": str(output_file), "profiles": profiles, "ranked": ranked}
