from __future__ import annotations

import json
from pathlib import Path

from common import BACKEND_DIR, banner, emit_and_save
from clustering.service import ClusteringService
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager
from integration.evidence_generator import EvidenceGenerator


def main() -> None:
    database = Database()
    database.initialize()
    repository = PublicationRepository(database)

    manager = IndexManager()
    try:
        manager.load()
    except FileNotFoundError:
        manager.build_from_publications(repository.list_all())

    generator = EvidenceGenerator(
        database=database,
        publication_repository=repository,
        index_manager=manager,
        clustering_service=ClusteringService(),
        output_dir=BACKEND_DIR / "docs" / "evidence",
    )
    result = generator.generate()
    evidence_path = Path(result["path"])
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    task1 = evidence.get("task1", {})
    task2 = evidence.get("task2", {}).get("metadata", {}).get("training_report", {})

    lines = [
        banner("SYSTEM EVIDENCE JSON — GENERATION + HIGHLIGHTS"),
        f"Generated evidence file: {evidence_path}",
        "",
        "Task 1 highlights",
        f"Publication count: {task1.get('publication_count')}",
        f"Index stats: {json.dumps(task1.get('index_stats', {}), ensure_ascii=False)}",
        f"Recent crawl runs: {json.dumps(task1.get('recent_crawl_runs', []), ensure_ascii=False)}",
        "",
        "Task 2 highlights",
        f"Dataset: {json.dumps(task2.get('dataset', {}), ensure_ascii=False)}",
        f"Evaluation: {json.dumps(task2.get('evaluation', {}), ensure_ascii=False)}",
        f"Cluster sizes: {json.dumps(task2.get('cluster_sizes', {}), ensure_ascii=False)}",
    ]

    emit_and_save("06_generate_system_evidence", lines)


if __name__ == "__main__":
    main()
