from urllib.parse import urlparse, urlunparse

from models.publication import Publication


class PublicationDeduplicator:
    def __init__(self):
        self.seen_urls = set()
        self.seen_titles = set()

    def _canonical_url(self, url: str) -> str:
        parsed = urlparse(url)
        return urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            "",
            "",
        ))

    def is_duplicate(self, publication: Publication) -> bool:
        url_key = self._canonical_url(publication.publication_url)
        title_key = " ".join(publication.title.lower().split())

        if url_key in self.seen_urls:
            return True

        if title_key and title_key in self.seen_titles:
            return True

        self.seen_urls.add(url_key)

        if title_key:
            self.seen_titles.add(title_key)

        return False
