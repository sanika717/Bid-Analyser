PROJECT_DIR = Path(__file__).parent
PDF_DIR = PROJECT_DIR / "pdfs"
TEMPLATE = PROJECT_DIR / "templates" / "template.xlsx"
OUTPUT_DIR = PROJECT_DIR / "output"

HEADER_VENDOR_START_COL = 6

MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "qwen2.5:1.5b"   # ✅ use lightweight model

EMBED_MODEL = None
