"""Keeps crawler URLs inside the allowed PurePortal scope and removes duplicate variants."""

from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

class URLFilter:
    def __init__(self, allowed_domain, allowed_path_prefixes):
        self.allowed_domain = allowed_domain.lower()
        self.allowed_path_prefixes = allowed_path_prefixes

    def canonicalize(self, url, base_url=None):
        if base_url:
            url = urljoin(base_url, url)

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return None

        host = (parsed.hostname or "").lower()
        if not host:
            return None

        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/") + "/"

        # Keep RSS pagination parameters, but remove tracking/sorting parameters that create duplicate URLs.
        query = parse_qs(parsed.query, keep_blank_values=False)
        page_values = query.get("page", [])
        canonical_parameters = []
        if query.get("format") == ["rss"]:
            canonical_parameters.append(("format", "rss"))
        if len(page_values) == 1 and page_values[0].isdigit():
            canonical_parameters.append(("page", int(page_values[0])))

        canonical_query = urlencode(canonical_parameters)

        return urlunparse(("https", host, path, "", canonical_query, ""))

    def is_allowed(self, url):
        parsed = urlparse(url)
        if (parsed.hostname or "").lower() != self.allowed_domain:
            return False
        return any(parsed.path.startswith(p) for p in self.allowed_path_prefixes)
