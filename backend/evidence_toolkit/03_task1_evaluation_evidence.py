from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import BACKEND_DIR, banner, emit_and_save
from database.database import Database
from database.publication_repository import PublicationRepository
from evaluation.search_evaluator import SearchEvaluator
from indexing.index_manager import IndexManager
from search.search_engine import SearchEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-run Task 1 retrieval evaluation and print its summary."
    )
    parser.add_argument(
        "--qrels",
        type=Path,
        default=BACKEND_DIR / "data" / "task1_qrels.json",
        help="Relevance-judgment JSON file.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=BACKEND_DIR / "data" / "evaluation" / "task1_evaluation.json",
        help="Full JSON report destination.",
    )
    args = parser.parse_args()

    database = Database()
    database.initialize()
    repository = PublicationRepository(database)

    manager = IndexManager()
    manager.load()

    evaluator = SearchEvaluator(SearchEngine(manager, repository))
    judgments = evaluator.load_judgments(args.qrels)
    report = evaluator.evaluate(judgments, k_values=(5, 10))
    evaluator.save_report(report, args.report)

    lines = [
        banner("TASK 1 — RETRIEVAL EVALUATION EVIDENCE"),
        f"Qrels: {args.qrels}",
        f"Full report: {args.report}",
        "",
        json.dumps(report["summary"], indent=2),
    ]
    emit_and_save("03_task1_evaluation_evidence", lines)


if __name__ == "__main__":
    main()
