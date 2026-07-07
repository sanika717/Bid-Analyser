from pathlib import Path
from openpyxl import load_workbook
from engine1.engine import fill_workbook


def write_excel(template_path: Path, profiles, out_path: Path):
    wb = load_workbook(template_path)
    wb = fill_workbook(wb, profiles)
    wb.save(out_path)
    return out_path
