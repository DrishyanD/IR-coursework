from dataclasses import dataclass, field

from models.publication import Publication


@dataclass
class SearchResult:
    publication: Publication
    score: float
    snippet: str = ""
    execution_time_ms: float | None = None
