from __future__ import annotations

import subprocess
import sys

from common import BACKEND_DIR, banner, emit_and_save


def main() -> None:
    command = [sys.executable, "-m", "pytest", "-q"]
    completed = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    lines = [
        banner("AUTOMATED TEST SUITE EVIDENCE"),
        f"Command: {' '.join(command)}",
        f"Exit code: {completed.returncode}",
        "",
        completed.stdout.rstrip(),
    ]
    emit_and_save("07_test_suite_evidence", lines)

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
