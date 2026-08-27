from pathlib import Path


class SystemValidator:
    def __init__(
        self,
        database,
        publication_repository,
        index_manager,
        clustering_service,
    ):
        self.database = database
        self.publication_repository = publication_repository
        self.index_manager = index_manager
        self.clustering_service = clustering_service

    def validate(self) -> dict:
        checks = {}

        checks["database_exists"] = Path(self.database.path).exists()
        checks["publication_count"] = self.publication_repository.count()
        checks["has_publications"] = checks["publication_count"] > 0

        index_stats = self.index_manager.stats()
        checks["index_documents"] = index_stats["documents"]
        checks["vocabulary_size"] = index_stats["vocabulary_size"]
        checks["index_matches_database"] = (
            checks["publication_count"] == checks["index_documents"]
        )

        clustering_status = self.clustering_service.status()
        checks["clustering_trained"] = clustering_status["trained"]

        checks["task1_ready"] = (
            checks["database_exists"]
            and checks["has_publications"]
            and checks["index_matches_database"]
            and checks["vocabulary_size"] > 0
        )

        checks["task2_ready"] = checks["clustering_trained"]
        checks["full_system_ready"] = (
            checks["task1_ready"]
            and checks["task2_ready"]
        )

        return checks
