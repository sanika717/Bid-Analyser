from pathlib import Path
import shutil
import tempfile
from typing import List

from engine1 import engine as legacy
from engine.llm import ollama_client


def run_bid_analysis(pdf_files: List[str], template_file: str):
    """
    Run bid analysis over a list of PDF file paths and a template file path.
    This function adapts the legacy engine1.engine.run_engine() to a reusable
    callable that doesn't depend on fixed project folders.
    """
    # create temporary dirs for PDFs and output
    work_dir = Path(tempfile.mkdtemp(prefix="bid_engine_"))
    pdf_dir = work_dir / "pdfs"
    out_dir = work_dir / "output"
    pdf_dir.mkdir()
    out_dir.mkdir()

    # copy PDFs into pdf_dir
    for p in pdf_files:
        shutil.copy(p, pdf_dir / Path(p).name)

    # ensure template exists
    tpl = Path(template_file)
    if not tpl.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    # monkeypatch legacy module globals
    legacy.PDF_DIR = pdf_dir
    legacy.OUTPUT_DIR = out_dir
    legacy.TEMPLATE = tpl

    # override legacy ollama caller to ensure centralization
    legacy.call_ollama = ollama_client.call_ollama

    # call legacy runner
    result = legacy.run_engine()

    # copy output file to a persistent project folder so it remains available
    output_file = Path(result.get("output_file"))
    if not output_file.exists():
        output_file = out_dir / output_file.name

    persistent_dir = Path(__file__).resolve().parent.parent / "output"
    persistent_dir.mkdir(exist_ok=True)
    persistent_file = persistent_dir / output_file.name
    shutil.copy(output_file, persistent_file)

    result["output_file"] = str(persistent_file)
    return result


# backward compatible name used by app.py
def run_engine(callback=None):
    # For local compatibility, run engine against local pdfs/ and templates/
    # fall back to legacy behavior.
    return legacy.run_engine(callback=callback)
