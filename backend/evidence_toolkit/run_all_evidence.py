from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from common import BACKEND_DIR, OUTPUT_DIR, banner


DEFAULT_SCRIPTS = [
    "01_task1_index_evidence.py",
    "02_task1_positional_phrase_evidence.py",
    "03_task1_evaluation_evidence.py",
    "04_task2_evidence.py",
    "05_system_smoke_evidence.py",
    "06_generate_system_evidence.py",
    "07_test_suite_evidence.py",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the reusable coursework evidence toolkit."
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest when you only need the quicker evidence set.",
    )
    args = parser.parse_args()

    scripts = list(DEFAULT_SCRIPTS)
    if args.skip_tests:
        scripts.remove("07_test_suite_evidence.py")

    toolkit_dir = Path(__file__).resolve().parent
    aggregate = [banner("COURSEWORK EVIDENCE TOOLKIT — FULL RUN")]
    any_failure = False

    for script_name in scripts:
        script_path = toolkit_dir / script_name
        heading = f"RUNNING {script_name}"
        print("\n" + banner(heading))
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        print(completed.stdout, end="")
        aggregate.extend(
            [
                "",
                banner(heading),
                f"Exit code: {completed.returncode}",
                completed.stdout.rstrip(),
            ]
        )
        if completed.returncode != 0:
            any_failure = True

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"all_evidence_{stamp}.txt"
    latest = OUTPUT_DIR / "all_evidence_latest.txt"
    text = "\n".join(aggregate).rstrip() + "\n"
    path.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")

    print(f"\nAggregate evidence saved: {path}")
    print(f"Latest aggregate copy:     {latest}")

    if any_failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
