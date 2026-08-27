from __future__ import annotations

import json

from common import banner, emit_and_save
from clustering.service import ClusteringService
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager
from integration.system_validator import SystemValidator
from search.search_engine import SearchEngine


def main() -> None:
    database = Database()
    database.initialize()
    repository = PublicationRepository(database)

    manager = IndexManager()
    try:
        manager.load()
    except FileNotFoundError:
        manager.build_from_publications(repository.list_all())

    clustering = ClusteringService()
    validator = SystemValidator(
        database=database,
        publication_repository=repository,
        index_manager=manager,
        clustering_service=clustering,
    )
    status = validator.validate()

    lines = [banner("FULL SYSTEM — SMOKE / INTEGRATION EVIDENCE"), "System status"]
    lines.extend(f"{key}: {value}" for key, value in status.items())

    if status.get("task1_ready"):
        engine = SearchEngine(manager, repository)
        results = engine.search("healthcare community", top_k=5)
        lines.extend(["", "Task 1 smoke search", f"Result count: {len(results)}"])
        for position, result in enumerate(results, start=1):
            lines.append(
                f"{position}. {result.publication.title} score={result.score:.6f}"
            )

    if status.get("task2_ready"):
        prediction = clustering.predict(
            "The central bank raised interest rates after inflation increased."
        )
        lines.extend(["", "Task 2 smoke prediction", json.dumps(prediction, indent=2)])

    emit_and_save("05_system_smoke_evidence", lines)


if __name__ == "__main__":
    main()
