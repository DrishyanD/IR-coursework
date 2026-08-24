from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR
load_dotenv(BACKEND_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    seed_url: str = (
        "https://pureportal.coventry.ac.uk/en/organisations/"
        "centre-for-healthcare-and-community-transformation/"
    )
    allowed_domain: str = "pureportal.coventry.ac.uk"
    target_organisation_name: str = "Centre for Healthcare and Community Transformation"
    target_organisation_path: str = (
        "/en/organisations/centre-for-healthcare-and-community-transformation/"
    )
    user_agent: str = "Softwarica-IR-Coursework-Crawler/1.0"
    request_timeout: int = 15
    crawl_delay: float = 2.0
    max_retries: int = 2
    max_pages: int = 250
    rss_urls: tuple[str, ...] = (
        seed_url + "publications/?format=rss",
        seed_url + "publications/?format=rss&page=1",
    )
    allowed_path_prefixes: tuple[str, ...] = (
        "/en/organisations/",
        "/en/publications/",
        "/en/persons/",
    )

    database_path: Path = PROJECT_DIR / "data" / "ir.sqlite3"

    openalex_api_key: str | None = os.getenv("OPENALEX_API_KEY")
    openalex_base_url: str = "https://api.openalex.org"

    scheduler_enabled: bool = True
    scheduler_timezone: str = "UTC"
    scheduler_day_of_week: str = "sun"
    scheduler_hour: int = 2
    scheduler_minute: int = 0

    # Optional local test fallback. Normal coursework runs leave this disabled.
    development_ignore_robots: bool = _env_bool("DEVELOPMENT_IGNORE_ROBOTS", False)


settings = Settings()
