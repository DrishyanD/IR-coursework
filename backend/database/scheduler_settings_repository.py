from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from database.database import Database


VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


class SchedulerSettingsRepository:
    def __init__(self, database: Database):
        self.database = database

    def get(self) -> dict:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM scheduler_settings WHERE id = 1"
            ).fetchone()

        if row is None:
            raise RuntimeError("Scheduler settings have not been initialized.")

        result = dict(row)
        result["enabled"] = bool(result["enabled"])
        return result

    @staticmethod
    def _validate(day_of_week: str, hour: int, minute: int, timezone: str):
        if day_of_week not in VALID_DAYS:
            raise ValueError("day_of_week must be one of mon, tue, wed, thu, fri, sat, sun.")
        if not 0 <= int(hour) <= 23:
            raise ValueError("hour must be between 0 and 23.")
        if not 0 <= int(minute) <= 59:
            raise ValueError("minute must be between 0 and 59.")
        try:
            ZoneInfo(timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("timezone must be a valid IANA timezone name.") from exc

    def update(
        self,
        enabled: bool | None = None,
        day_of_week: str | None = None,
        hour: int | None = None,
        minute: int | None = None,
        timezone: str | None = None,
    ) -> dict:
        current = self.get()
        next_enabled = current["enabled"] if enabled is None else bool(enabled)
        next_day = current["day_of_week"] if day_of_week is None else day_of_week.strip().lower()
        next_hour = current["hour"] if hour is None else int(hour)
        next_minute = current["minute"] if minute is None else int(minute)
        next_timezone = current["timezone"] if timezone is None else timezone.strip()

        self._validate(next_day, next_hour, next_minute, next_timezone)

        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE scheduler_settings
                SET enabled = ?, day_of_week = ?, hour = ?, minute = ?,
                    timezone = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
                """,
                (
                    int(next_enabled),
                    next_day,
                    next_hour,
                    next_minute,
                    next_timezone,
                ),
            )

        return self.get()
