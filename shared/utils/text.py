import re


def normalize_code(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"(?:kod|code)\s*[:\-]?\s*(\d{1,32})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"#(\d{1,32})", text)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{1,32})\b", text)
    if m:
        return m.group(1)
    return None


def strip_code_from_caption(text: str, code: str) -> str:
    if not text:
        return ""
    text = re.sub(rf"(?i)\b(kod|code)\s*[:\-]?\s*{re.escape(code)}\b", "", text)
    text = re.sub(rf"#{re.escape(code)}\b", "", text)
    text = re.sub(rf"(?m)^\s*{re.escape(code)}\s*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text
