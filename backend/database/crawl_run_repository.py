from database.database import Database


class CrawlRunRepository:
    def __init__(self, database: Database):
        self.database = database

    def start(self, trigger_type: str = "manual") -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO crawl_runs (status, trigger_type)
                VALUES ('running', ?)
                """,
                (trigger_type,),
            )
            return int(cursor.lastrowid)

    def finish(self, run_id: int, summary: dict):
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE crawl_runs
                SET
                    finished_at = CURRENT_TIMESTAMP,
                    status = 'completed',
                    pages_fetched = ?,
                    pages_failed = ?,
                    robots_blocked = ?,
                    publications_seen = ?,
                    publications_inserted = ?,
                    publications_updated = ?,
                    publications_changed = ?,
                    publications_unchanged = ?,
                    publications_rejected = ?,
                    index_documents = ?,
                    error_message = NULL
                WHERE id = ?
                """,
                (
                    summary.get("pages_fetched", 0),
                    summary.get("pages_failed", 0),
                    summary.get("robots_blocked", 0),
                    summary.get("publications_seen", 0),
                    summary.get("publications_inserted", 0),
                    summary.get("publications_updated", 0),
                    summary.get("publications_changed", 0),
                    summary.get("publications_unchanged", 0),
                    summary.get("publications_rejected", 0),
                    summary.get("index_documents", 0),
                    run_id,
                ),
            )

    def fail(self, run_id: int, error_message: str):
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE crawl_runs
                SET
                    finished_at = CURRENT_TIMESTAMP,
                    status = 'failed',
                    error_message = ?
                WHERE id = ?
                """,
                (error_message[:2000], run_id),
            )

    def stop(self, run_id: int, summary: dict):
        self.finish(run_id, summary)
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE crawl_runs SET status = 'stopped' WHERE id = ?",
                (run_id,),
            )

    def stop_orphaned_runs(self) -> int:
        """Close runs left open when the previous backend process exited."""
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE crawl_runs
                SET finished_at = CURRENT_TIMESTAMP,
                    status = 'stopped',
                    error_message = 'Backend stopped before the crawl could finish.'
                WHERE status = 'running'
                """
            )
        return cursor.rowcount

    def get(self, run_id: int):
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM crawl_runs WHERE id = ?",
                (run_id,),
            ).fetchone()

        return dict(row) if row else None

    def latest(self, limit: int = 20):
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM crawl_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]
