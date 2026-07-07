from pathlib import Path

from engine.template.template_parser import extract_template_requirements


def read_template(path: Path):
    return {
        "path": str(path),
        "requirements": extract_template_requirements(path),
    }
