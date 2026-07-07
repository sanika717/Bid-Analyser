from pathlib import Path
from typing import Optional
import shutil

STORAGE_DIR = Path.cwd() / "storage_data"
STORAGE_DIR.mkdir(exist_ok=True)


def save_file(file_path: str, dest_subpath: Optional[str] = None) -> str:
    """Save an existing file into storage area and return the stored path."""
    src = Path(file_path)
    if dest_subpath:
        dest = STORAGE_DIR / dest_subpath
    else:
        dest = STORAGE_DIR / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dest)
    return str(dest)


def read_file(path: str) -> bytes:
    p = Path(path)
    return p.read_bytes()


def get_output_file(job_id: str) -> Optional[str]:
    # naive mapping: look for files starting with job_id
    for f in STORAGE_DIR.glob(f"{job_id}*"):
        return str(f)
    return None
