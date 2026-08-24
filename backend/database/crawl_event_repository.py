from database.database import Database


class CrawlEventRepository:
    def __init__(self, database: Database):
        self.database = database

    def add(
        self,
        run_id: int,
        level: str,
        event_type: str,
        message: str,
        url: str | None = None,
    ) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO crawl_events (run_id, level, event_type, message, url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, level.upper(), event_type.upper(), message[:1000], url),
            )
            return int(cursor.lastrowid)

    def list_for_run(self, run_id: int, after_id: int = 0, limit: int = 500):
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM crawl_events
                WHERE run_id = ? AND id > ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (run_id, after_id, limit),
            ).fetchall()

        return [dict(row) for row in rows]
