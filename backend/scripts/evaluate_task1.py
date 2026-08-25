import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json

from config import PROJECT_DIR
from database.database import Database
from database.publication_repository import PublicationRepository
from evaluation.search_evaluator import SearchEvaluator
from indexing.index_manager import IndexManager
from search.search_engine import SearchEngine


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Task 1 ranked retrieval using manual relevance judgments."
    )
    parser.add_argument(
        "--qrels",
        default=PROJECT_DIR / "data" / "task1_qrels.json",
        help="Path to JSON relevance judgments.",
    )
    parser.add_argument(
        "--output",
        default=PROJECT_DIR / "data" / "evaluation" / "task1_evaluation.json",
        help="Path for the evaluation report.",
    )
    args = parser.parse_args()

    database = Database()
    database.initialize()

    repository = PublicationRepository(database)
    index_manager = IndexManager()
    index_manager.load()

    engine = SearchEngine(index_manager, repository)
    evaluator = SearchEvaluator(engine)

    qrels_path = Path(args.qrels)
    judgments = evaluator.load_judgments(qrels_path)
    report = evaluator.evaluate(judgments, k_values=(5, 10))
    evaluator.save_report(report, args.output)

    print(json.dumps(report["summary"], indent=2))
    print(f"\nSaved full report to: {args.output}")


if __name__ == "__main__":
    main()
