from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from engine.template.template_parser import extract_template_requirements


def _normalize_field_name(label: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return cleaned or "value"


def extract_semi_structured_values(text: str, template_path: str | None = None) -> Dict[str, str]:
    values: Dict[str, str] = {}
    template_file = Path(template_path) if template_path else Path("templates/template.xlsx")
    template_requirements = extract_template_requirements(template_file)
    for line in text.splitlines():
        for requirement in template_requirements:
            key = _normalize_field_name(requirement)
            if key in values:
                continue
            patterns = [
                rf"{re.escape(requirement)}\s*[:\-–]\s*(.+)",
                rf"{re.escape(requirement)}\s+(.+)",
            ]
            for pattern_text in patterns:
                match = re.search(pattern_text, line, re.IGNORECASE)
                if match:
                    value = re.sub(r"\s+", " ", match.group(1)).strip(" .;:,")
                    if value:
                        values[key] = value
                    break
    return values
