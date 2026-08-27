import json
from datetime import datetime, timezone
from pathlib import Path

from database.crawl_run_repository import CrawlRunRepository


class EvidenceGenerator:
    def __init__(
        self,
        database,
        publication_repository,
        index_manager,
        clustering_service,
        output_dir,
    ):
        self.database = database
        self.publication_repository = publication_repository
        self.index_manager = index_manager
        self.clustering_service = clustering_service
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self) -> dict:
        publications = self.publication_repository.list_all()
        public_run_fields = {
            "id", "started_at", "finished_at", "status", "pages_fetched",
            "pages_failed", "robots_blocked", "publications_seen",
            "publications_inserted", "publications_updated",
            "publications_changed", "publications_unchanged",
            "publications_rejected", "index_documents", "error_message",
            "trigger_type",
        }
        crawl_runs = [
            {key: value for key, value in run.items() if key in public_run_fields}
            for run in CrawlRunRepository(self.database).latest(20)
        ]

        sample_publications = [
            {
                "id": publication.id,
                "title": publication.title,
                "year": publication.year,
                "authors": [author.name for author in publication.authors],
                "publication_url": publication.publication_url,
                "author_profile_urls": publication.author_profile_urls,
                "keywords": publication.keywords,
                "output_type": publication.output_type,
                "doi": publication.doi,
            }
            for publication in publications[:10]
        ]

        sample_terms = []
        for term in sorted(self.index_manager.inverted_index.postings)[:20]:
            sample_terms.append(
                {
                    "term": term,
                    "document_frequency": (
                        self.index_manager.inverted_index.document_frequency(term)
                    ),
                    "postings": (
                        self.index_manager.inverted_index.get_postings(term)
                    ),
                }
            )

        clustering_status = self.clustering_service.status()
        clustering_metadata = None

        if clustering_status["trained"]:
            try:
                clustering_metadata = self.clustering_service.load()
            except Exception:
                clustering_metadata = {
                    "error": "Clustering artifacts exist but could not be loaded."
                }

        evidence = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "task1": {
                "publication_count": len(publications),
                "index_stats": self.index_manager.stats(),
                "sample_publications": sample_publications,
                "sample_inverted_index_terms": sample_terms,
                "recent_crawl_runs": crawl_runs,
            },
            "task2": {
                "status": clustering_status,
                "metadata": clustering_metadata,
            },
        }

        output_path = self.output_dir / "system_evidence.json"
        output_path.write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "path": str(output_path),
            "evidence": evidence,
        }
