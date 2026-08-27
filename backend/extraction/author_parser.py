import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from extraction.cleaner import clean_text
from models.author import Author


class AuthorParser:
    def parse_publication_authors(self, soup: BeautifulSoup, page_url: str) -> list[Author]:
        authors = []
        seen = set()

        byline = soup.select_one(".introduction ul.relations.persons")
        if not byline:
            return authors

        for item in byline.find_all("li", recursive=False):
            anchor = item.find("a", href=True)
            name = clean_text(
                anchor.get_text(" ", strip=True)
                if anchor
                else item.get_text(" ", strip=True)
            )
            name = re.sub(r"^[\s,;&]+|[\s,;&]+$", "", name)
            if not name:
                continue

            profile_url = None
            if anchor:
                candidate_url = urljoin(page_url, anchor["href"])
                path_parts = [part for part in urlparse(candidate_url).path.split("/") if part]
                if len(path_parts) >= 3 and path_parts[:2] == ["en", "persons"]:
                    profile_url = candidate_url

            key = name.casefold()

            if key in seen:
                continue

            seen.add(key)
            authors.append(Author(name=name, profile_url=profile_url))

        return authors

    def parse_profile(self, html: str, page_url: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        h1 = soup.find("h1")

        name = clean_text(h1.get_text(" ", strip=True)) if h1 else ""
        organisations = []
        organisation_urls = []
        seen = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            if "/en/organisations/" not in href:
                continue

            text = clean_text(anchor.get_text(" ", strip=True))
            url = urljoin(page_url, href)

            if url in seen:
                continue

            seen.add(url)
            organisations.append(text)
            organisation_urls.append(url)

        return {
            "name": name,
            "profile_url": page_url,
            "organisations": organisations,
            "organisation_urls": organisation_urls,
        }
