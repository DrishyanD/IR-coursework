import html
import re

def clean_text(value: str | None) -> str:
    if not value:
        return ""

    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()
