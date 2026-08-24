"""Database operations for storing, updating and reading publication records."""

import hashlib
import json
from database.author_repository import AuthorRepository
from database.database import Database
from models.author import Author
from models.publication import Publication


class PublicationRepository:
    def __init__(self, database: Database):
        self.database = database
        self.author_repository = AuthorRepository(database)

    @classmethod
    def compute_content_hash(cls, publication: Publication) -> str:
        """Deterministically hash the core content fields to detect changes.

        Keywords are sorted to ensure the same keywords in a different order
        produce the same hash.
        """
        title = publication.title.strip() if publication.title else ""
        abstract = publication.abstract.strip() if publication.abstract else ""
        keywords = sorted([k.strip().lower() for k in publication.keywords])
        keywords_str = "|".join(keywords)
        topics_str = "|".join(sorted(topic.strip().lower() for topic in publication.openalex_topics))

        payload = (
            f"{title}|{publication.publication_date or ''}|{abstract}|{keywords_str}|{publication.openalex_id or ''}|"
            f"{publication.cited_by_count}|{publication.is_open_access}|"
            f"{publication.open_access_url or ''}|{topics_str}"
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def upsert(self, publication: Publication) -> int:
        new_hash = self.compute_content_hash(publication)

        payload = (
            publication.title.strip(),
            publication.year,
            publication.publication_date,
            publication.abstract,
            json.dumps(publication.keywords, ensure_ascii=False),
            json.dumps(publication.organisations, ensure_ascii=False),
            json.dumps(publication.organisation_urls, ensure_ascii=False),
            publication.output_type,
            publication.doi,
            publication.openalex_id,
            publication.cited_by_count,
            publication.is_open_access,
            publication.open_access_url,
            json.dumps(publication.openalex_topics, ensure_ascii=False),
            new_hash,
        )

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, content_hash
                FROM publications
                WHERE publication_url = ?
                """,
                (publication.publication_url,),
            ).fetchone()

            if row:
                publication_id = int(row["id"])
                old_hash = row["content_hash"]
                changed = old_hash != new_hash

                connection.execute(
                    """
                    UPDATE publications
                    SET
                        title = ?,
                        year = ?,
                        publication_date = ?,
                        abstract = ?,
                        keywords_json = ?,
                        organisations_json = ?,
                        organisation_urls_json = ?,
                        output_type = ?,
                        doi = ?,
                        openalex_id = ?,
                        cited_by_count = ?,
                        is_open_access = ?,
                        open_access_url = ?,
                        openalex_topics_json = ?,
                        content_hash = ?,
                        last_seen_at = CURRENT_TIMESTAMP,
                        last_changed_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE last_changed_at END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (*payload, changed, publication_id),
                )
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO publications (
                        title,
                        year,
                        publication_date,
                        abstract,
                        keywords_json,
                        organisations_json,
                        organisation_urls_json,
                        output_type,
                        doi,
                        openalex_id,
                        cited_by_count,
                        is_open_access,
                        open_access_url,
                        openalex_topics_json,
                        content_hash,
                        first_seen_at,
                        last_seen_at,
                        last_changed_at,
                        publication_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                    """,
                    (*payload, publication.publication_url),
                )
                publication_id = int(cursor.lastrowid)

        self._replace_authors(publication_id, publication.authors)
        return publication_id

    def _replace_authors(self, publication_id: int, authors: list[Author]):
        author_ids = []

        for position, author in enumerate(authors):
            author_id = self.author_repository.upsert(author)
            author_ids.append((author_id, position))

        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM publication_authors WHERE publication_id = ?",
                (publication_id,),
            )

            connection.executemany(
                """
                INSERT OR IGNORE INTO publication_authors (
                    publication_id,
                    author_id,
                    author_order
                )
                VALUES (?, ?, ?)
                """,
                [
                    (publication_id, author_id, position)
                    for author_id, position in author_ids
                ],
            )

    def get_by_id(self, publication_id: int) -> Publication | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM publications
                WHERE id = ?
                """,
                (publication_id,),
            ).fetchone()

            if not row:
                return None

            author_rows = connection.execute(
                """
                SELECT a.id, a.name, a.profile_url
                FROM authors a
                JOIN publication_authors pa
                    ON pa.author_id = a.id
                WHERE pa.publication_id = ?
                ORDER BY pa.author_order
                """,
                (publication_id,),
            ).fetchall()

        return self._row_to_publication(row, author_rows)

    def get_by_url(self, publication_url: str) -> Publication | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM publications
                WHERE publication_url = ?
                """,
                (publication_url,),
            ).fetchone()

        if not row:
            return None

        return self.get_by_id(int(row["id"]))

    def list_all(self) -> list[Publication]:
        with self.database.connect() as connection:
            pub_rows = connection.execute(
                """
                SELECT *
                FROM publications
                ORDER BY year DESC, title ASC
                """
            ).fetchall()

            if not pub_rows:
                return []

            # Load all publication-author links at once to avoid one query per publication.
            author_rows = connection.execute(
                """
                SELECT pa.publication_id, a.id, a.name, a.profile_url
                FROM publication_authors pa
                JOIN authors a ON pa.author_id = a.id
                ORDER BY pa.publication_id, pa.author_order
                """
            ).fetchall()

        # Group the rows by publication ID before building model objects.
        from collections import defaultdict
        authors_by_pub: dict[int, list] = defaultdict(list)
        for ar in author_rows:
            authors_by_pub[int(ar["publication_id"])].append(ar)

        publications = []
        for row in pub_rows:
            pub_id = int(row["id"])
            pub_author_rows = authors_by_pub.get(pub_id, [])
            publications.append(self._row_to_publication(row, pub_author_rows))

        return publications

    def count(self) -> int:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM publications"
            ).fetchone()

        return int(row["total"])

    def delete_by_url(self, publication_url: str) -> bool:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM publications
                WHERE publication_url = ?
                """,
                (publication_url,),
            )

        return cursor.rowcount > 0

    def _row_to_publication(self, row, author_rows) -> Publication:
        authors = [
            Author(
                id=int(author["id"]),
                name=author["name"],
                profile_url=author["profile_url"],
            )
            for author in author_rows
        ]

        return Publication(
            id=int(row["id"]),
            title=row["title"],
            publication_url=row["publication_url"],
            authors=authors,
            year=row["year"],
            publication_date=(
                row["publication_date"] if "publication_date" in row.keys() else None
            ),
            abstract=row["abstract"],
            keywords=json.loads(row["keywords_json"] or "[]"),
            organisations=json.loads(row["organisations_json"] or "[]"),
            organisation_urls=json.loads(row["organisation_urls_json"] or "[]"),
            output_type=row["output_type"],
            doi=row["doi"],
            openalex_id=row["openalex_id"] if "openalex_id" in row.keys() else None,
            cited_by_count=row["cited_by_count"] if "cited_by_count" in row.keys() else None,
            is_open_access=(
                bool(row["is_open_access"])
                if "is_open_access" in row.keys() and row["is_open_access"] is not None
                else None
            ),
            open_access_url=row["open_access_url"] if "open_access_url" in row.keys() else None,
            openalex_topics=(
                json.loads(row["openalex_topics_json"] or "[]")
                if "openalex_topics_json" in row.keys()
                else []
            ),
            content_hash=row["content_hash"] if "content_hash" in row.keys() else None,
            first_seen_at=row["first_seen_at"] if "first_seen_at" in row.keys() else None,
            last_seen_at=row["last_seen_at"] if "last_seen_at" in row.keys() else None,
            last_changed_at=row["last_changed_at"] if "last_changed_at" in row.keys() else None,
        )
