"""Runs a publication update from crawling through storage and index rebuilding."""

import logging
import threading
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from config import settings
from crawler.crawler import CoventryCrawler
from crawler.openalex_client import OpenAlexClient
from database.crawl_run_repository import CrawlRunRepository
from database.crawl_event_repository import CrawlEventRepository
from extraction.author_parser import AuthorParser
from extraction.membership_validator import MembershipValidator
from extraction.publication_parser import PublicationParser


logger = logging.getLogger(__name__)


class CrawlUpdateService:
    def __init__(
        self,
        database,
        publication_repository,
        index_manager,
        search_engine=None,
    ):
        self.database = database
        self.publication_repository = publication_repository
        self.index_manager = index_manager
        self.search_engine = search_engine
        self.run_repository = CrawlRunRepository(database)
        self.event_repository = CrawlEventRepository(database)
        self.publication_parser = PublicationParser()
        self.author_parser = AuthorParser()
        self.membership_validator = MembershipValidator()
        self.openalex_client = OpenAlexClient()
        self._run_lock = threading.Lock()
        self._stop_requested = threading.Event()
        self.current_run_id = None

    def _is_target_organisation_root(self, url: str) -> bool:
        path = urlparse(url).path.rstrip("/")
        target = settings.target_organisation_path.rstrip("/")
        return path == target

    def _is_publication_page(self, url: str) -> bool:
        parts = [part for part in urlparse(url).path.split("/") if part]
        return len(parts) == 3 and parts[:2] == ["en", "publications"]

    def _is_rss_page(self, url: str) -> bool:
        return "format=rss" in urlparse(url).query.lower()

    def _record_event(self, run_id, level, event_type, message, url=None):
        self.event_repository.add(run_id, level, event_type, message, url)

    def request_stop(self) -> bool:
        if self.current_run_id is None:
            return False
        self._stop_requested.set()
        return True

    def _queue_focused_links(self, crawler: CoventryCrawler, html: str, current_url: str):
        if self._is_rss_page(current_url):
            soup = BeautifulSoup(html, "xml")
            candidates = [item.find("link") for item in soup.find_all("item")]
            hrefs = [link.get_text(strip=True) for link in candidates if link]
        else:
            soup = BeautifulSoup(html, "html.parser")
            hrefs = [anchor["href"] for anchor in soup.find_all("a", href=True)]

        queued = 0
        for href in hrefs:
            url = crawler.url_filter.canonicalize(href, current_url)

            if not url:
                continue

            if not crawler.url_filter.is_allowed(url):
                continue

            # RSS gives the publication links, so other organisation tabs are skipped to avoid extra requests.
            if self._is_target_organisation_root(url) or self._is_publication_page(url):
                if crawler.frontier.add(url):
                    queued += 1

        if self._is_rss_page(current_url):
            self._record_event(
                self.current_run_id,
                "info",
                "rss_discovery",
                f"RSS feed added {queued} publication links to the crawl queue.",
                current_url,
            )

    def _profile_confirms_membership(self, crawler: CoventryCrawler, publication) -> bool:
        for author in publication.authors:
            if not author.profile_url:
                continue

            profile_url = crawler.url_filter.canonicalize(author.profile_url)

            if not profile_url:
                continue

            if not crawler.url_filter.is_allowed(profile_url):
                continue

            html = crawler.fetch(profile_url)

            if not html:
                continue

            profile = self.author_parser.parse_profile(html, profile_url)

            if self.membership_validator.profile_matches(profile):
                return True

        return False

    def _publication_is_in_scope(self, crawler: CoventryCrawler, publication) -> bool:
        if self.membership_validator.publication_matches(publication):
            return True

        return self._profile_confirms_membership(crawler, publication)

    def _enrich_from_openalex(self, publication, event_callback) -> bool:
        if not publication.doi:
            return False

        try:
            enrichment = self.openalex_client.lookup_by_doi(publication.doi)
        except Exception as exc:
            event_callback(
                "warning",
                "openalex",
                f"OpenAlex enrichment failed: {type(exc).__name__}.",
                publication.publication_url,
            )
            return False

        if not enrichment:
            event_callback(
                "info",
                "openalex",
                "No OpenAlex work matched this publication DOI.",
                publication.publication_url,
            )
            return False

        publication.openalex_id = enrichment["openalex_id"]
        publication.cited_by_count = enrichment["cited_by_count"]
        publication.is_open_access = enrichment["is_open_access"]
        publication.open_access_url = enrichment["open_access_url"]
        publication.openalex_topics = enrichment["topics"]

        # Keep PurePortal as the main source and use OpenAlex only to fill missing metadata.
        publication.abstract = publication.abstract or enrichment["abstract"]
        publication.year = publication.year or enrichment["publication_year"]
        publication.publication_date = (
            publication.publication_date or enrichment["publication_date"]
        )
        publication.output_type = publication.output_type or enrichment["work_type"]
        event_callback(
            "success",
            "openalex",
            "Publication metadata was enriched from OpenAlex using its DOI.",
            publication.publication_url,
        )
        return True

    @staticmethod
    def _retain_existing_enrichment(publication, existing):
        if existing is None:
            return
        publication.openalex_id = existing.openalex_id
        publication.cited_by_count = existing.cited_by_count
        publication.is_open_access = existing.is_open_access
        publication.open_access_url = existing.open_access_url
        publication.openalex_topics = existing.openalex_topics
        publication.publication_date = (
            publication.publication_date or existing.publication_date
        )

    def run(self, trigger_type: str = "manual") -> dict:
        self.database.initialize()

        if not self._run_lock.acquire(blocking=False):
            raise RuntimeError("A publication crawl is already running.")

        run_id = self.run_repository.start(trigger_type)
        self.current_run_id = run_id
        self._stop_requested.clear()

        summary = {
            "run_id": run_id,
            "pages_fetched": 0,
            "pages_failed": 0,
            "robots_blocked": 0,
            "publications_seen": 0,
            "publications_inserted": 0,
            "publications_updated": 0,
            "publications_changed": 0,
            "publications_unchanged": 0,
            "publications_rejected": 0,
            "publications_enriched": 0,
            "index_documents": 0,
        }

        def event_callback(level, event_type, message, url=None):
            self._record_event(run_id, level, event_type, message, url)

        crawler = CoventryCrawler(event_callback=event_callback)

        try:
            event_callback(
                "info",
                "start",
                f"{trigger_type.capitalize()} publication crawl started.",
                settings.seed_url,
            )

            crawler.prepare()

            while (
                len(crawler.frontier)
                and len(crawler.frontier.visited) < settings.max_pages
            ):
                if self._stop_requested.is_set():
                    event_callback("warning", "stop", "The crawl was stopped by an administrator.")
                    break

                url = crawler.frontier.next()

                if url is None:
                    break

                html = crawler.fetch(url)
                crawler.frontier.mark_visited(url)

                if not html:
                    continue

                if self._is_publication_page(url):
                    summary["publications_seen"] += 1

                    publication = self.publication_parser.parse(html, url)

                    if not publication.title:
                        summary["publications_rejected"] += 1
                        event_callback("warning", "reject", "Publication page had no title.", url)
                        continue

                    if not self._publication_is_in_scope(crawler, publication):
                        summary["publications_rejected"] += 1
                        event_callback("info", "reject", "Publication did not match the target organisation.", url)
                        continue

                    existing = self.publication_repository.get_by_url(
                        publication.publication_url
                    )
                    self._retain_existing_enrichment(publication, existing)
                    if self._enrich_from_openalex(publication, event_callback):
                        summary["publications_enriched"] += 1

                    publication.id = self.publication_repository.upsert(publication)

                    if existing is None:
                        summary["publications_inserted"] += 1
                        event_callback("success", "insert", f"Stored publication: {publication.title}", url)
                    else:
                        old_hash = existing.content_hash
                        new_hash = self.publication_repository.compute_content_hash(publication)
                        if old_hash != new_hash:
                            summary["publications_changed"] += 1
                            summary["publications_updated"] += 1
                            event_callback("success", "update", f"Updated publication: {publication.title}", url)
                        else:
                            summary["publications_unchanged"] += 1

                self._queue_focused_links(crawler, html, url)

            summary["pages_fetched"] = crawler.stats.pages_fetched
            summary["pages_failed"] = crawler.stats.pages_failed
            summary["robots_blocked"] = crawler.stats.robots_blocked

            publications = self.publication_repository.list_all()
            self.index_manager.build_from_publications(publications)
            self.index_manager.save()
            if self.search_engine is not None:
                self.search_engine.refresh_index_references()

            summary["index_documents"] = (
                self.index_manager.inverted_index.document_count
            )

            if self._stop_requested.is_set():
                self.run_repository.stop(run_id, summary)
            else:
                self.run_repository.finish(run_id, summary)
                event_callback(
                    "success",
                    "complete",
                    f"Crawl completed with {summary['index_documents']} indexed publications.",
                )

            logger.info("Crawl/update completed: %s", summary)
            return summary

        except Exception as exc:
            self.run_repository.fail(run_id, str(exc))
            event_callback("error", "failed", f"Crawl failed: {str(exc)}")
            logger.exception("Crawl/update failed")
            raise
        finally:
            self.current_run_id = None
            self._stop_requested.clear()
            self._run_lock.release()
