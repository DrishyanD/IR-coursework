import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

# Direct script execution starts Python inside scripts/, so add the backend root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager


def is_canonical_publication_url(url: str) -> bool:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    return (
        parsed.hostname == "pureportal.coventry.ac.uk"
        and parts[:2] == ["en", "publications"]
        and len(parts) == 3
        and not parsed.query
        and not parsed.fragment
    )


def find_invalid_subpages(database: Database) -> tuple[int, list[dict]]:
    with database.connect() as connection:
        rows = connection.execute(
            "SELECT id, publication_url FROM publications ORDER BY id"
        ).fetchall()

    flagged = []
    for row in rows:
        parsed = urlparse(row["publication_url"])
        parts = [part for part in parsed.path.split("/") if part]
        if parts[:2] == ["en", "publications"] and len(parts) > 3:
            flagged.append(dict(row))

    return len(rows), flagged


def cleanup(database: Database, index_manager: IndexManager, dry_run: bool) -> dict:
    examined, flagged = find_invalid_subpages(database)
    removed = 0

    if not dry_run and flagged:
        with database.connect() as connection:
            placeholders = ",".join("?" for _ in flagged)
            cursor = connection.execute(
                f"DELETE FROM publications WHERE id IN ({placeholders})",
                tuple(row["id"] for row in flagged),
            )
            removed = cursor.rowcount

        repository = PublicationRepository(database)
        index_manager.build_from_publications(repository.list_all())
        index_manager.save()

    with database.connect() as connection:
        remaining = connection.execute(
            "SELECT COUNT(*) AS total FROM publications"
        ).fetchone()["total"]
        urls = [
            row["publication_url"]
            for row in connection.execute("SELECT publication_url FROM publications")
        ]

    return {
        "rows_examined": examined,
        "rows_flagged": len(flagged),
        "urls_flagged": [row["publication_url"] for row in flagged],
        "rows_removed": removed,
        "remaining_publications": remaining,
        "remaining_canonical_publications": sum(
            is_canonical_publication_url(url) for url in urls
        ),
    }


def print_summary(result: dict):
    print(f"Rows examined: {result['rows_examined']}")
    print(f"Rows flagged: {result['rows_flagged']}")
    print("URLs flagged:")
    for url in result["urls_flagged"]:
        print(f"  {url}")
    print(f"Rows removed: {result['rows_removed']}")
    print(f"Remaining publication count: {result['remaining_publications']}")
    print(
        "Remaining distinct canonical publication count: "
        f"{result['remaining_canonical_publications']}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Remove stored PurePortal publication subpages from Task 1 data."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Show rows without deleting them.")
    mode.add_argument("--execute", action="store_true", help="Delete flagged rows and rebuild the index.")
    args = parser.parse_args()

    database = Database()
    database.initialize()
    result = cleanup(database, IndexManager(), dry_run=args.dry_run)
    print_summary(result)


if __name__ == "__main__":
    main()
