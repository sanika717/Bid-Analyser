from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from engine.template.template_parser import extract_template_requirements


def _normalize_field_name(label: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return cleaned or "value"


def extract_structured_values(text: str, template_path: str | None = None) -> Dict[str, str]:
    values: Dict[str, str] = {}
    template_file = Path(template_path) if template_path else Path("templates/template.xlsx")
    template_requirements = extract_template_requirements(template_file)
    for requirement in template_requirements:
        if not requirement:
            continue
        pattern = re.compile(rf"{re.escape(requirement)}", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            snippet = text[max(0, match.start() - 80):match.end() + 200].strip()
            snippet = re.sub(r"\s+", " ", snippet)
            values[_normalize_field_name(requirement)] = snippet
    return values
