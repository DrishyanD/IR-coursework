from urllib.parse import urlparse

from config import settings
from models.publication import Publication


class MembershipValidator:
    def __init__(
        self,
        target_name: str | None = None,
        target_path: str | None = None,
    ):
        self.target_name = (target_name or settings.target_organisation_name).lower()
        self.target_path = target_path or settings.target_organisation_path

    def publication_matches(self, publication: Publication) -> bool:
        for name in publication.organisations:
            if self.target_name in name.lower():
                return True

        for url in publication.organisation_urls:
            if urlparse(url).path.rstrip("/") == self.target_path.rstrip("/"):
                return True

        return False

    def profile_matches(self, profile: dict) -> bool:
        for name in profile.get("organisations", []):
            if self.target_name in name.lower():
                return True

        for url in profile.get("organisation_urls", []):
            if urlparse(url).path.rstrip("/") == self.target_path.rstrip("/"):
                return True

        return False
