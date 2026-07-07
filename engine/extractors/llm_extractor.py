from engine1.engine import llm_extract


def llm_extract_wrapper(text: str, need_vendor: bool, missing_fields: list):
    return llm_extract(text, need_vendor, missing_fields)
