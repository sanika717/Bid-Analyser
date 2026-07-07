from pathlib import Path
from engine1.engine import read_pdf_text, extract_tables


def read_text(path: Path) -> str:
    return read_pdf_text(path)


def extract_table_list(path: Path):
    return extract_tables(path)
