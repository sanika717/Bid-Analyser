from engine1.engine import extract_vendor_name


def vendor_name(text: str, tables: list, filename: str):
    return extract_vendor_name(text, tables, filename)
