from models.search_result import SearchResult


class Ranker:
    def rank(
        self,
        scored_publications: list[SearchResult],
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        filtered = [
            result
            for result in scored_publications
            if result.score > min_score
        ]

        filtered.sort(
            key=lambda result: (
                -result.score,
                -(result.publication.year or 0),
                result.publication.title.lower(),
            )
        )

        return filtered[:top_k]
