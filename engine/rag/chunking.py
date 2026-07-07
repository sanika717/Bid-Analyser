from __future__ import annotations

import re
from typing import List


def section_chunk(text: str, max_chars: int = 900) -> List[str]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []

    sections = []
    for match in re.finditer(r"(?im)^(#{0,3}\s*)([A-Za-z][A-Za-z0-9 /&()\-]+)$", cleaned):
        pass

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    current = []
    current_len = 0
    for line in lines:
        if re.match(r"^(commercial|technical|price|delivery|warranty|tax|payment|terms|scope|summary|appendix)", line, re.I):
            if current:
                sections.append("\n".join(current).strip())
                current = []
                current_len = 0
            current.append(line)
            current_len = len(line)
            continue

        if current_len + len(line) > max_chars and current:
            sections.append("\n".join(current).strip())
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line)

    if current:
        sections.append("\n".join(current).strip())

    return [section for section in sections if len(section.split()) >= 8]
