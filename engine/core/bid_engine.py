from typing import List
from pathlib import Path
from engine1.engine import run_engine as legacy_run


def run_bid_analysis(pdf_files: List[str], template_file: str):
    # Delegate to engine.__init__.run_bid_analysis for consistent behavior
    from engine import run_bid_analysis as pkg_run
    return pkg_run(pdf_files, template_file)
