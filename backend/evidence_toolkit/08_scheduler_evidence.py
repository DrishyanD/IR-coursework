from __future__ import annotations

"""Verified scheduler evidence for the ST7071CEM coursework.

Place this file in ``backend/evidence_toolkit/`` and run it from the backend
folder with:

    python evidence_toolkit/08_scheduler_evidence.py

It reports the persisted weekly schedule, verifies the live scheduler endpoint
through FastAPI's application lifespan, and shows the latest recorded scheduled
crawl if one exists.  It does not start a crawl itself.
"""

import json
import sys
from pathlib import Path

# Support both the intended backend/evidence_toolkit location and a standalone
# copy launched from the backend directory.
THIS_FILE = Path(__file__).resolve()
if THIS_FILE.parent.name == "evidence_toolkit":
    TOOLKIT_DIR = THIS_FILE.parent
    BACKEND_DIR = TOOLKIT_DIR.parent
else:
    BACKEND_DIR = Path.cwd().resolve()
    TOOLKIT_DIR = BACKEND_DIR / "evidence_toolkit"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if TOOLKIT_DIR.exists() and str(TOOLKIT_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLKIT_DIR))

try:
    from common import banner, emit_and_save  # type: ignore
except ImportError:
    from datetime import datetime

    OUTPUT_DIR = BACKEND_DIR / "docs" / "evidence" / "toolkit"

    def banner(title: str) -> str:
        line = "=" * 72
        return f"{line}\n{title}\n{line}"

    def emit_and_save(stem: str, lines: list[str]) -> str:
        text = "\n".join(str(line) for line in lines)
        print(text)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stamped = OUTPUT_DIR / f"{stem}_{stamp}.txt"
        latest = OUTPUT_DIR / f"{stem}_latest.txt"
        stamped.write_text(text.rstrip() + "\n", encoding="utf-8")
        latest.write_text(text.rstrip() + "\n", encoding="utf-8")
        print(f"\nSaved evidence: {stamped}")
        print(f"Latest copy:    {latest}")
        return text

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from database.database import Database
from database.scheduler_settings_repository import SchedulerSettingsRepository


def _latest_scheduled_run(database: Database) -> dict | None:
    # CrawlRunRepository does not need a special method just for evidence, so
    # use the same database connection and keep this read-only.
    with database.connect() as connection:
        row = connection.execute(
            """
            SELECT id, started_at, finished_at, status, pages_fetched,
                   pages_failed, robots_blocked, publications_seen,
                   publications_inserted, publications_updated,
                   publications_changed, publications_unchanged,
                   publications_rejected, index_documents, trigger_type,
                   error_message
            FROM crawl_runs
            WHERE trigger_type = 'scheduled'
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row is not None else None


def _calculated_next_run(configuration: dict) -> str | None:
    if not configuration.get("enabled"):
        return None
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    tz = ZoneInfo(configuration["timezone"])
    now = datetime.now(tz)
    target_weekday = day_map[configuration["day_of_week"]]
    days_ahead = (target_weekday - now.weekday()) % 7
    candidate = (now + timedelta(days=days_ahead)).replace(
        hour=int(configuration["hour"]),
        minute=int(configuration["minute"]),
        second=0,
        microsecond=0,
    )
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate.isoformat()


def _live_scheduler_response() -> tuple[dict | None, str | None]:
    try:
        from fastapi.testclient import TestClient
        from main import app
        with TestClient(app) as client:
            response = client.get("/api/admin/scheduler")
            response.raise_for_status()
            return response.json(), None
    except Exception as exc:  # lets the evidence script still show persisted config
        return None, f"{type(exc).__name__}: {exc}"


def main() -> None:
    database = Database()
    database.initialize()
    persisted = SchedulerSettingsRepository(database).get()
    runtime, runtime_error = _live_scheduler_response()
    scheduled_run = _latest_scheduled_run(database)

    lines = [
        banner("TASK 1 — AUTOMATIC SCHEDULER RUNTIME EVIDENCE"),
        "Persisted scheduler configuration",
        f"Enabled:          {persisted['enabled']}",
        "Frequency:        weekly",
        f"Day of week:      {persisted['day_of_week']}",
        f"Time:             {int(persisted['hour']):02d}:{int(persisted['minute']):02d}",
        f"Timezone:         {persisted['timezone']}",
        f"Last configured:  {persisted.get('updated_at')}",
        "",
        "Calculated next weekly run from persisted configuration",
        str(_calculated_next_run(persisted)),
        "",
        "Live FastAPI /api/admin/scheduler response",
        json.dumps(runtime, indent=2) if runtime is not None else f"Unavailable: {runtime_error}",
        "",
        "Latest recorded scheduled crawl",
    ]

    if scheduled_run is None:
        lines.extend([
            "No scheduled crawl has been recorded yet.",
            "To capture scheduled-execution evidence, set the schedule in the",
            "Data Management UI to a time a few minutes ahead, keep the backend",
            "running, wait for the job to execute, then run this script again.",
        ])
    else:
        lines.append(json.dumps(scheduled_run, indent=2))

    lines.extend([
        "",
        "Verification note",
        "Manual updates and automatic weekly updates are independent controls,",
        "but both execute the same crawl/update/index-refresh service.",
    ])

    emit_and_save("08_scheduler_evidence", lines)


if __name__ == "__main__":
    main()
