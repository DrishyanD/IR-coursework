from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path


TOOLKIT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TOOLKIT_DIR.parent
OUTPUT_DIR = BACKEND_DIR / "docs" / "evidence" / "toolkit"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def banner(title: str) -> str:
    line = "=" * 72
    return f"{line}\n{title}\n{line}"


def save_text(stem: str, text: str) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stamped = OUTPUT_DIR / f"{stem}_{stamp}.txt"
    latest = OUTPUT_DIR / f"{stem}_latest.txt"
    stamped.write_text(text.rstrip() + "\n", encoding="utf-8")
    latest.write_text(text.rstrip() + "\n", encoding="utf-8")
    return stamped, latest


def emit_and_save(stem: str, lines: list[str]) -> str:
    text = "\n".join(str(line) for line in lines)
    print(text)
    stamped, latest = save_text(stem, text)
    print(f"\nSaved evidence: {stamped}")
    print(f"Latest copy:    {latest}")
    return text
