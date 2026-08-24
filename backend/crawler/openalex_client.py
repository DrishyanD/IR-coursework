from urllib.parse import unquote

import requests

from config import settings


class OpenAlexClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.openalex_api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    @staticmethod
    def _normalise_doi(doi: str) -> str:
        value = unquote(doi).strip()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if value.lower().startswith(prefix):
                value = value[len(prefix):]
                break
        return value.strip().lower()

    @staticmethod
    def _abstract(inverted_index) -> str | None:
        if not isinstance(inverted_index, dict):
            return None

        positioned_words = []
        for word, positions in inverted_index.items():
            if not isinstance(positions, list):
                continue
            positioned_words.extend((position, word) for position in positions)

        if not positioned_words:
            return None
        return " ".join(word for _, word in sorted(positioned_words))

    def lookup_by_doi(self, doi: str) -> dict | None:
        normalised_doi = self._normalise_doi(doi)
        if not normalised_doi:
            return None

        params = {
            "filter": f"doi:https://doi.org/{normalised_doi}",
            "per-page": 1,
        }
        if self.api_key:
            params["api_key"] = self.api_key

        response = self.session.get(
            f"{settings.openalex_base_url}/works",
            params=params,
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return None

        work = results[0]
        open_access = work.get("open_access") or {}
        best_location = work.get("best_oa_location") or {}
        topics = [
            item.get("display_name")
            for item in work.get("topics", [])
            if item.get("display_name")
        ]

        return {
            "openalex_id": work.get("id"),
            "cited_by_count": work.get("cited_by_count"),
            "is_open_access": open_access.get("is_oa"),
            "open_access_url": (
                best_location.get("pdf_url")
                or best_location.get("landing_page_url")
                or open_access.get("oa_url")
            ),
            "topics": topics,
            "abstract": self._abstract(work.get("abstract_inverted_index")),
            "publication_year": work.get("publication_year"),
            "publication_date": work.get("publication_date"),
            "work_type": work.get("type_crossref") or work.get("type"),
        }
