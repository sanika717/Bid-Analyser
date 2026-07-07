from pathlib import Path
import os

BASE_DIR = Path.cwd()
PDF_DIR = BASE_DIR / "pdfs"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE = BASE_DIR / "templates" / "template.xlsx"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
