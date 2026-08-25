import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clustering.service import ClusteringService
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager
from integration.system_validator import SystemValidator
from search.search_engine import SearchEngine


def main():
    database = Database()
    database.initialize()

    repository = PublicationRepository(database)
    index_manager = IndexManager()

    try:
        index_manager.load()
    except FileNotFoundError:
        index_manager.build_from_publications(repository.list_all())

    clustering_service = ClusteringService()

    validator = SystemValidator(
        database=database,
        publication_repository=repository,
        index_manager=index_manager,
        clustering_service=clustering_service,
    )

    status = validator.validate()

    print("System status")
    for key, value in status.items():
        print(f"{key}: {value}")

    if status["task1_ready"]:
        engine = SearchEngine(index_manager, repository)
        results = engine.search("healthcare community", top_k=5)

        print("\nTask 1 smoke search")
        print("Result count:", len(results))

        for position, result in enumerate(results, start=1):
            print(
                f"{position}. {result.publication.title} "
                f"score={result.score:.6f}"
            )
    else:
        print(
            "\nTask 1 is not ready yet. "
            "Run the real crawl/update first."
        )

    if status["task2_ready"]:
        service = ClusteringService()
        prediction = service.predict(
            "The central bank raised interest rates after inflation increased."
        )

        print("\nTask 2 smoke prediction")
        print(prediction)
    else:
        print(
            "\nTask 2 is not ready yet. "
            "Train the real clustering dataset first."
        )


if __name__ == "__main__":
    main()
