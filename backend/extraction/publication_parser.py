"""Extracts publication metadata from Coventry PurePortal publication pages."""

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from extraction.author_parser import AuthorParser
from extraction.cleaner import clean_text
from models.publication import Publication


class PublicationParser:
    def __init__(self):
        self.author_parser = AuthorParser()

    def parse(self, html: str, page_url: str) -> Publication:
        soup = BeautifulSoup(html, "html.parser")

        title = self._title(soup)
        authors = self.author_parser.parse_publication_authors(soup, page_url)
        organisations, organisation_urls = self._organisations(soup, page_url)

        return Publication(
            title=title,
            publication_url=page_url,
            authors=authors,
            year=self._year(soup),
            publication_date=self._publication_date(soup),
            abstract=self._section_text(soup, "Abstract"),
            keywords=self._keywords(soup),
            organisations=organisations,
            organisation_urls=organisation_urls,
            output_type=self._output_type(soup),
            doi=self._doi(soup),
        )

    def _title(self, soup: BeautifulSoup) -> str:
        h1 = soup.find("h1")
        return clean_text(h1.get_text(" ", strip=True)) if h1 else ""

    def _organisations(self, soup: BeautifulSoup, page_url: str):
        names = []
        urls = []
        seen = set()

        for item in soup.select(".introduction ul.relations.organisations > li"):
            anchor = item.find("a", href=True)
            name = clean_text(item.get_text(" ", strip=True))
            key = name.casefold()
            if not name or key in seen:
                continue

            seen.add(key)
            names.append(name)

            if anchor and "/en/organisations/" in anchor.get("href", ""):
                urls.append(urljoin(page_url, anchor["href"]))

        return names, urls

    @staticmethod
    def _normalise_publication_date(value: str) -> str | None:
        """Return a stable ISO-like publication date (YYYY-MM-DD / YYYY-MM)."""
        text = clean_text(value)
        if not text:
            return None

        # PurePortal uses several date formats, so try the common numeric and month-name forms.
        numeric = re.search(r"\b((?:19|20)\d{2})[-/]([01]?\d)(?:[-/]([0-3]?\d))?\b", text)
        if numeric:
            year, month, day = numeric.groups()
            if day:
                try:
                    return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            try:
                return datetime(int(year), int(month), 1).strftime("%Y-%m")
            except ValueError:
                pass

        for fmt in ("%d %b %Y", "%d %B %Y"):
            match = re.search(
                r"\b([0-3]?\d\s+[A-Za-z]{3,9}\s+(?:19|20)\d{2})\b",
                text,
            )
            if match:
                try:
                    return datetime.strptime(match.group(1), fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue

        for fmt in ("%b %Y", "%B %Y"):
            match = re.search(r"\b([A-Za-z]{3,9}\s+(?:19|20)\d{2})\b", text)
            if match:
                try:
                    return datetime.strptime(match.group(1), fmt).strftime("%Y-%m")
                except ValueError:
                    continue

        return None

    def _publication_date(self, soup: BeautifulSoup) -> str | None:
        for key in ("citation_publication_date", "citation_date", "dc.date"):
            meta = soup.find("meta", attrs={"name": key})
            if meta and meta.get("content"):
                value = self._normalise_publication_date(meta["content"])
                if value:
                    return value

        text = soup.get_text(" ", strip=True)
        date_patterns = (
            r"Early online date\s*([^|]{0,50}?(?:19|20)\d{2})",
            r"Publication status\s*[^|]{0,80}?[-–]\s*([^|]{0,40}?(?:19|20)\d{2})",
        )
        for pattern in date_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                value = self._normalise_publication_date(match.group(1))
                if value:
                    return value

        return None

    def _year(self, soup: BeautifulSoup) -> int | None:
        for key in ("citation_publication_date", "citation_date", "dc.date"):
            meta = soup.find("meta", attrs={"name": key})
            if meta and meta.get("content"):
                match = re.search(r"\b(19|20)\d{2}\b", meta["content"])
                if match:
                    return int(match.group())

        text = soup.get_text(" ", strip=True)

        patterns = (
            r"Publication status\s*Published\s*-?\s*[^\d]*(20\d{2})",
            r"Early online date\s*[^\d]*(20\d{2})",
            r"\b(20\d{2})\b",
        )

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _section_text(self, soup: BeautifulSoup, heading: str) -> str | None:
        header = soup.find(
            lambda tag: tag.name in {"h2", "h3"}
            and clean_text(tag.get_text(" ", strip=True)).lower() == heading.lower()
        )

        if not header:
            return None

        parts = []
        for sibling in header.find_next_siblings():
            if sibling.name in {"h2", "h3"}:
                break

            text = clean_text(sibling.get_text(" ", strip=True))
            if text:
                parts.append(text)

        value = clean_text(" ".join(parts))
        return value or None

    def _keywords(self, soup: BeautifulSoup) -> list[str]:
        header = soup.find(
            lambda tag: tag.name in {"h2", "h3"}
            and clean_text(tag.get_text(" ", strip=True)).lower() == "keywords"
        )

        if not header:
            return []

        keywords = []
        seen = set()

        for sibling in header.find_next_siblings():
            if sibling.name in {"h2", "h3"}:
                break

            values = sibling.find_all(["li", "span"])
            if not values:
                values = [sibling]

            for item in values:
                text = clean_text(item.get_text(" ", strip=True))
                if text and text.lower() not in seen:
                    seen.add(text.lower())
                    keywords.append(text)

        return keywords

    def _output_type(self, soup: BeautifulSoup) -> str | None:
        text = soup.get_text(" ", strip=True)
        match = re.search(
            r"Research output:\s*(.*?)(?=\s{2,}|Abstract|Original language|\Z)",
            text,
            flags=re.IGNORECASE,
        )
        return clean_text(match.group(1)) if match else None

    def _doi(self, soup: BeautifulSoup) -> str | None:
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if "doi.org/" in href:
                return href.split("doi.org/", 1)[1].strip("/ ")

        text = soup.get_text(" ", strip=True)
        match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.IGNORECASE)
        return match.group(0).rstrip(".,;)") if match else None
