from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class ArticleLoader:
    """Load a public BBC News article for Task 2 cluster assignment."""

    ALLOWED_HOSTS = {"bbc.com", "www.bbc.com", "bbc.co.uk", "www.bbc.co.uk"}

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def load(self, url: str) -> dict:
        self._validate_url(url)
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Softwarica-IR-Coursework/1.0"},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise ValueError(f"BBC returned HTTP {status} for this article URL.") from exc
        except requests.RequestException as exc:
            raise ValueError("The BBC article could not be downloaded.") from exc

        self._validate_url(response.url)
        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("The URL did not return an HTML article.")

        payload = getattr(response, "content", None) or response.text
        soup = BeautifulSoup(payload, "html.parser")
        article = soup.find("article") or soup.find("main")
        if article is None:
            raise ValueError("No article content was found on this BBC page.")

        heading = article.find("h1")
        title = heading.get_text(" ", strip=True) if heading else ""
        paragraphs = []
        seen = set()
        for paragraph in article.find_all("p"):
            text = paragraph.get_text(" ", strip=True)
            key = text.casefold()
            if len(text) < 20 or key in seen:
                continue
            seen.add(key)
            paragraphs.append(text)

        text = " ".join(part for part in [title, *paragraphs] if part).strip()
        if len(text) < 20:
            raise ValueError("The BBC page did not contain enough article text.")

        return {"title": title or None, "text": text[:100_000], "url": response.url}

    def _validate_url(self, url: str):
        parsed = urlparse(url)
        if parsed.scheme != "https" or (parsed.hostname or "").lower() not in self.ALLOWED_HOSTS:
            raise ValueError("Enter a public HTTPS BBC News article URL.")
