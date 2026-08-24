from dataclasses import dataclass, field

from models.author import Author


@dataclass
class Publication:
    title: str
    publication_url: str
    authors: list[Author] = field(default_factory=list)
    year: int | None = None
    publication_date: str | None = None
    abstract: str | None = None
    keywords: list[str] = field(default_factory=list)
    organisations: list[str] = field(default_factory=list)
    organisation_urls: list[str] = field(default_factory=list)
    output_type: str | None = None
    doi: str | None = None
    openalex_id: str | None = None
    cited_by_count: int | None = None
    is_open_access: bool | None = None
    open_access_url: str | None = None
    openalex_topics: list[str] = field(default_factory=list)
    id: int | None = None
    content_hash: str | None = None
    first_seen_at: str | None = None
    last_seen_at: str | None = None
    last_changed_at: str | None = None

    @property
    def author_profile_urls(self) -> list[str]:
        return [
            author.profile_url
            for author in self.authors
            if author.profile_url
        ]
