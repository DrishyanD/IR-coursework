from dataclasses import dataclass


@dataclass
class Author:
    name: str
    profile_url: str | None = None
    id: int | None = None
