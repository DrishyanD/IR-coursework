import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse

from clustering.service import ClusteringService
from config import PROJECT_DIR
from crawler.update_service import CrawlUpdateService
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager
from integration.evidence_generator import EvidenceGenerator
from integration.system_validator import SystemValidator


def main():
    parser = argparse.ArgumentParser(
        description="Run the real integrated coursework backend pipeline."
    )
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        help="Do not run the real Coventry crawl.",
    )
    parser.add_argument(
        "--skip-clustering",
        action="store_true",
        help="Do not train Task 2.",
    )
    parser.add_argument(
        "--clustering-data",
        default=str(PROJECT_DIR / "data" / "clustering" / "documents.csv"),
        help="Path to the real Task 2 dataset.",
    )
    args = parser.parse_args()

    database = Database()
    database.initialize()

    repository = PublicationRepository(database)
    index_manager = IndexManager()

    if not args.skip_crawl:
        print("Running Task 1 crawl/update...")
        update_service = CrawlUpdateService(
            database=database,
            publication_repository=repository,
            index_manager=index_manager,
        )
        crawl_summary = update_service.run()
        print("Crawl/update complete:")
        print(crawl_summary)
    else:
        try:
            index_manager.load()
        except FileNotFoundError:
            index_manager.build_from_publications(repository.list_all())
            index_manager.save()

    clustering_service = ClusteringService()

    if not args.skip_clustering:
        clustering_path = Path(args.clustering_data)

        if clustering_path.exists():
            print("\nTraining Task 2 clustering model...")
            report = clustering_service.train_from_csv(
                clustering_path,
                minimum_documents=100,
            )
            print("Task 2 training complete.")
            print("Evaluation:", report["evaluation"])
        else:
            print(
                "\nTask 2 dataset not found at:",
                clustering_path,
            )

    validator = SystemValidator(
        database=database,
        publication_repository=repository,
        index_manager=index_manager,
        clustering_service=clustering_service,
    )

    print("\nFinal system validation:")
    status = validator.validate()
    for key, value in status.items():
        print(f"{key}: {value}")

    evidence = EvidenceGenerator(
        database=database,
        publication_repository=repository,
        index_manager=index_manager,
        clustering_service=clustering_service,
        output_dir=PROJECT_DIR / "docs" / "evidence",
    )

    result = evidence.generate()

    print("\nEvidence file:")
    print(result["path"])


if __name__ == "__main__":
    main()
