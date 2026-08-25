import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crawler.update_service import CrawlUpdateService
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager


def main():
    database = Database()
    database.initialize()

    repository = PublicationRepository(database)
    index_manager = IndexManager()

    service = CrawlUpdateService(
        database=database,
        publication_repository=repository,
        index_manager=index_manager,
    )

    summary = service.run()

    print("\nCrawl/update summary")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
