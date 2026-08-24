from database.database import Database
from models.author import Author


class AuthorRepository:
    def __init__(self, database: Database):
        self.database = database

    def upsert(self, author: Author) -> int:
        name = author.name.strip()
        profile_url = author.profile_url.strip() if author.profile_url else None

        if profile_url:
            with self.database.connect() as connection:
                row = connection.execute(
                    "SELECT id FROM authors WHERE profile_url = ?",
                    (profile_url,),
                ).fetchone()

                if row:
                    connection.execute(
                        """
                        UPDATE authors
                        SET name = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (name, row["id"]),
                    )
                    return int(row["id"])

                cursor = connection.execute(
                    """
                    INSERT INTO authors (name, profile_url)
                    VALUES (?, ?)
                    """,
                    (name, profile_url),
                )
                return int(cursor.lastrowid)

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM authors
                WHERE name = ? AND profile_url IS NULL
                """,
                (name,),
            ).fetchone()

            if row:
                return int(row["id"])

            cursor = connection.execute(
                """
                INSERT INTO authors (name, profile_url)
                VALUES (?, NULL)
                """,
                (name,),
            )
            return int(cursor.lastrowid)

    def get_by_id(self, author_id: int) -> Author | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, name, profile_url
                FROM authors
                WHERE id = ?
                """,
                (author_id,),
            ).fetchone()

        if not row:
            return None

        return Author(
            id=int(row["id"]),
            name=row["name"],
            profile_url=row["profile_url"],
        )

    def get_by_profile_url(self, profile_url: str) -> Author | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, name, profile_url
                FROM authors
                WHERE profile_url = ?
                """,
                (profile_url,),
            ).fetchone()

        if not row:
            return None

        return Author(
            id=int(row["id"]),
            name=row["name"],
            profile_url=row["profile_url"],
        )

    def list_all(self) -> list[Author]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, profile_url
                FROM authors
                ORDER BY name
                """
            ).fetchall()

        return [
            Author(
                id=int(row["id"]),
                name=row["name"],
                profile_url=row["profile_url"],
            )
            for row in rows
        ]
