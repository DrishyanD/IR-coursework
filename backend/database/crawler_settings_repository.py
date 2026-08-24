from database.database import Database


class CrawlerSettingsRepository:
    def __init__(self, database: Database):
        self.database = database

    def get(self) -> dict:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM crawler_settings WHERE id = 1"
            ).fetchone()

        if row is None:
            raise RuntimeError("Crawler settings have not been initialized.")

        result = dict(row)
        result["crawler_enabled"] = bool(result["crawler_enabled"])
        return result

    def update(
        self,
        crawler_enabled: bool | None = None,
        robots_mode: str | None = None,
    ) -> dict:
        current = self.get()
        enabled = current["crawler_enabled"] if crawler_enabled is None else crawler_enabled
        mode = current["robots_mode"] if robots_mode is None else robots_mode

        if mode not in {"enforce", "override"}:
            raise ValueError("robots_mode must be either 'enforce' or 'override'.")

        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE crawler_settings
                SET crawler_enabled = ?, robots_mode = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
                """,
                (int(enabled), mode),
            )

        return self.get()
