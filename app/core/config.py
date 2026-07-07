import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
OUTPUT_DIR = STORAGE_DIR / "outputs"
TEMPLATE_STORAGE = STORAGE_DIR / "templates"
STATIC_DIR = BASE_DIR / "backend" / "static"
PAGE_DIR = STATIC_DIR
DB_PATH = STORAGE_DIR / "db.sqlite"
EMAIL_LOG_DIR = STORAGE_DIR / "emails"
TEMPLATE_PATH = TEMPLATE_STORAGE / "template.xlsx"

JWT_SECRET = os.environ.get("TCE_JWT_SECRET", "tce-secret-key-change-me")
JWT_ALGORITHM = "HS256"
PASSWORD_RESET_URL = os.environ.get("PASSWORD_RESET_URL", "http://127.0.0.1:8000/reset")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@tce.com")
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))

for path in [STORAGE_DIR, UPLOAD_DIR, OUTPUT_DIR, TEMPLATE_STORAGE, EMAIL_LOG_DIR, STATIC_DIR]:
    path.mkdir(parents=True, exist_ok=True)
