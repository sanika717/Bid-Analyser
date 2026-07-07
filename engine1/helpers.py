def clean(x):
    if not x:
        return ""
    return re.sub(r"\s+", " ", html.unescape(str(x))).strip()

def norm(x):
    return clean(x).lower()

def short(x, n=200):
    return clean(x)[:n]

def clean_excel_safe(text):
    if not text:
        return ""
    text = re.sub(r"[\x00-\x1F]", "", str(text))
    return re.sub(r"\s+", " ", text).strip()
