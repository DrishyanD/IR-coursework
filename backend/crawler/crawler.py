"""Polite crawler used to collect pages from the configured Coventry PurePortal area."""

from dataclasses import dataclass
import logging
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

from config import settings
from crawler.frontier import URLFrontier
from crawler.rate_limiter import RateLimiter
from crawler.robots import RobotsChecker
from crawler.url_filter import URLFilter


logger = logging.getLogger(__name__)


@dataclass
class CrawlStats:
    pages_fetched: int = 0
    pages_failed: int = 0
    robots_blocked: int = 0
    duplicate_links: int = 0
    discovered_links: int = 0


class CoventryCrawler:
    def __init__(self, event_callback=None):
        self.event_callback = event_callback
        self.stats = CrawlStats()
        self.frontier = URLFrontier()
        self.url_filter = URLFilter(
            settings.allowed_domain,
            settings.allowed_path_prefixes,
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

        seed = urlsplit(settings.seed_url)
        base_url = urlunsplit((seed.scheme, seed.netloc, "", "", ""))
        self.robots = RobotsChecker(
            base_url,
            settings.user_agent,
            settings.request_timeout,
        )
        self.rate_limiter = RateLimiter(settings.crawl_delay)

    def _event(self, level, event_type, message, url=None):
        if self.event_callback:
            self.event_callback(level, event_type, message, url)

    @staticmethod
    def _request_error_message(exc):
        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            status = exc.response.status_code
            reason = exc.response.reason or "Unknown response"
            retry_after = exc.response.headers.get("Retry-After")
            message = f"PurePortal returned HTTP {status} {reason}."
            if retry_after:
                message += f" Retry-After: {retry_after}."
            return message

        if isinstance(exc, requests.Timeout):
            return f"The request timed out after {settings.request_timeout} seconds."

        if isinstance(exc, requests.ConnectionError):
            return "Could not connect to PurePortal."

        return f"Request failed: {type(exc).__name__}."

    def prepare(self):
        robots_loaded = self.robots.load()
        if not robots_loaded and not settings.development_ignore_robots:
            raise RuntimeError("Could not load robots.txt. Crawl stopped safely.")

        if robots_loaded:
            self._event(
                "info",
                "policy",
                "robots.txt loaded successfully.",
                self.robots.robots_url,
            )
        elif settings.development_ignore_robots:
            # This fallback is only for local testing. Normal coursework runs keep it disabled.
            logger.warning("Development robots fallback is active because robots.txt could not be loaded.")

        robots_delay = self.robots.crawl_delay() if robots_loaded else None
        if robots_delay is not None:
            self.rate_limiter.delay = max(
                self.rate_limiter.delay,
                float(robots_delay),
            )

        seed = self.url_filter.canonicalize(settings.seed_url)
        if not seed or not self.url_filter.is_allowed(seed):
            raise ValueError("Seed URL is outside the configured crawl scope.")
        self.frontier.add(seed)
        for rss_url in settings.rss_urls:
            canonical_rss_url = self.url_filter.canonicalize(rss_url)
            if canonical_rss_url and self.url_filter.is_allowed(canonical_rss_url):
                self.frontier.add(canonical_rss_url)

    def fetch(self, url):
        allowed_by_robots = self.robots.can_fetch(url)
        if not allowed_by_robots and not settings.development_ignore_robots:
            self.stats.robots_blocked += 1
            self._event("warning", "blocked", "robots.txt blocked this URL.", url)
            return None

        if not allowed_by_robots and settings.development_ignore_robots:
            logger.debug("Development robots fallback permitted URL: %s", url)

        for attempt in range(settings.max_retries + 1):
            try:
                self.rate_limiter.wait()
                response = self.session.get(url, timeout=settings.request_timeout)
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()
                supported_types = (
                    "text/html",
                    "application/rss+xml",
                    "application/xml",
                    "text/xml",
                )
                if not any(value in content_type for value in supported_types):
                    self._event(
                        "warning",
                        "content_type",
                        f"Skipped unsupported response type: {content_type or 'unknown'}.",
                        url,
                    )
                    return None

                self.stats.pages_fetched += 1
                self._event(
                    "info",
                    "fetch",
                    f"Fetched page with HTTP {response.status_code}.",
                    url,
                )
                return response.text
            except requests.RequestException as exc:
                message = self._request_error_message(exc)
                if attempt == settings.max_retries:
                    self.stats.pages_failed += 1
                    self._event(
                        "error",
                        "fetch",
                        f"{message} Request failed after {attempt + 1} attempts.",
                        url,
                    )
                    return None

                self._event(
                    "warning",
                    "retry",
                    f"{message} Retrying ({attempt + 2}/{settings.max_retries + 1}).",
                    url,
                )

    def discover_links(self, html, current_url):
        soup = BeautifulSoup(html, "html.parser")

        for anchor in soup.find_all("a", href=True):
            url = self.url_filter.canonicalize(anchor["href"], current_url)
            if not url or not self.url_filter.is_allowed(url):
                continue

            self.stats.discovered_links += 1
            if not self.frontier.add(url):
                self.stats.duplicate_links += 1

    def crawl(self):
        self.prepare()

        while len(self.frontier) and len(self.frontier.visited) < settings.max_pages:
            url = self.frontier.next()
            if url is None:
                break

            html = self.fetch(url)
            self.frontier.mark_visited(url)

            if html:
                print(f"[OK] {url}")
                self.discover_links(html, url)
            else:
                print(f"[SKIP] {url}")

        return self.stats


if __name__ == "__main__":
    crawler = CoventryCrawler()
    stats = crawler.crawl()
    print("\nCrawl complete")
    print(f"Fetched: {stats.pages_fetched}")
    print(f"Failed: {stats.pages_failed}")
    print(f"Robots blocked: {stats.robots_blocked}")
    print(f"Links discovered: {stats.discovered_links}")
    print(f"Duplicate links: {stats.duplicate_links}")
