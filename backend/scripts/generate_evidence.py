import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from clustering.service import ClusteringService
from config import PROJECT_DIR
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager
from integration.evidence_generator import EvidenceGenerator


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

    generator = EvidenceGenerator(
        database=database,
        publication_repository=repository,
        index_manager=index_manager,
        clustering_service=clustering_service,
        output_dir=PROJECT_DIR / "docs" / "evidence",
    )

    result = generator.generate()

    print("Evidence generated:")
    print(result["path"])


if __name__ == "__main__":
    main()
