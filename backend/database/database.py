"""SQLite connection and schema setup for publications, crawl history and scheduler settings."""

import sqlite3
from pathlib import Path

from config import settings


class Database:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or settings.database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    publication_url TEXT NOT NULL UNIQUE,
                    year INTEGER,
                    publication_date TEXT,
                    abstract TEXT,
                    keywords_json TEXT NOT NULL DEFAULT '[]',
                    organisations_json TEXT NOT NULL DEFAULT '[]',
                    organisation_urls_json TEXT NOT NULL DEFAULT '[]',
                    output_type TEXT,
                    doi TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    profile_url TEXT UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS publication_authors (
                    publication_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    author_order INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (publication_id, author_id),
                    FOREIGN KEY (publication_id)
                        REFERENCES publications(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (author_id)
                        REFERENCES authors(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS crawl_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    finished_at TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    pages_fetched INTEGER NOT NULL DEFAULT 0,
                    pages_failed INTEGER NOT NULL DEFAULT 0,
                    robots_blocked INTEGER NOT NULL DEFAULT 0,
                    publications_seen INTEGER NOT NULL DEFAULT 0,
                    publications_inserted INTEGER NOT NULL DEFAULT 0,
                    publications_updated INTEGER NOT NULL DEFAULT 0,
                    publications_rejected INTEGER NOT NULL DEFAULT 0,
                    index_documents INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT
                );

                CREATE TABLE IF NOT EXISTS scheduler_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    enabled INTEGER NOT NULL DEFAULT 1,
                    day_of_week TEXT NOT NULL DEFAULT 'sun',
                    hour INTEGER NOT NULL DEFAULT 2,
                    minute INTEGER NOT NULL DEFAULT 0,
                    timezone TEXT NOT NULL DEFAULT 'UTC',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                INSERT OR IGNORE INTO scheduler_settings (
                    id, enabled, day_of_week, hour, minute, timezone
                ) VALUES (1, 1, 'sun', 2, 0, 'UTC');

                CREATE TABLE IF NOT EXISTS crawl_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    url TEXT,
                    FOREIGN KEY (run_id) REFERENCES crawl_runs(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_publications_year
                    ON publications(year);

                CREATE INDEX IF NOT EXISTS idx_publications_doi
                    ON publications(doi);

                CREATE INDEX IF NOT EXISTS idx_authors_name
                    ON authors(name);

                CREATE INDEX IF NOT EXISTS idx_publication_authors_author
                    ON publication_authors(author_id);

                CREATE INDEX IF NOT EXISTS idx_crawl_runs_started_at
                    ON crawl_runs(started_at);

                CREATE INDEX IF NOT EXISTS idx_crawl_events_run_id
                    ON crawl_events(run_id, id);
                """
            )

            # Add newer content-tracking columns when an older database is opened.
            migrations = [
                "ALTER TABLE publications ADD COLUMN publication_date TEXT;",
                "ALTER TABLE publications ADD COLUMN content_hash TEXT;",
                "ALTER TABLE publications ADD COLUMN first_seen_at TEXT;",
                "ALTER TABLE publications ADD COLUMN last_seen_at TEXT;",
                "ALTER TABLE publications ADD COLUMN last_changed_at TEXT;",
                "ALTER TABLE crawl_runs ADD COLUMN trigger_type TEXT NOT NULL DEFAULT 'manual';",
                "ALTER TABLE crawl_runs ADD COLUMN publications_changed INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE crawl_runs ADD COLUMN publications_unchanged INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE publications ADD COLUMN openalex_id TEXT;",
                "ALTER TABLE publications ADD COLUMN cited_by_count INTEGER;",
                "ALTER TABLE publications ADD COLUMN is_open_access INTEGER;",
                "ALTER TABLE publications ADD COLUMN open_access_url TEXT;",
                "ALTER TABLE publications ADD COLUMN openalex_topics_json TEXT NOT NULL DEFAULT '[]';",
            ]
            
            for statement in migrations:
                try:
                    connection.execute(statement)
                except sqlite3.OperationalError:
                    # Duplicate-column errors simply mean this migration was already applied.
                    pass

    def clear_all(self):
        with self.connect() as connection:
            connection.execute("DELETE FROM publication_authors")
            connection.execute("DELETE FROM authors")
            connection.execute("DELETE FROM publications")
            connection.execute("DELETE FROM crawl_events")
            connection.execute("DELETE FROM crawl_runs")
