import argparse
import json
import sys
from pathlib import Path

# Make direct execution from backend/scripts work as documented.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clustering.service import ClusteringService
from config import PROJECT_DIR


def main():
    parser = argparse.ArgumentParser(
        description="Train the Task 2 TF-IDF + K-Means clustering model."
    )
    parser.add_argument(
        "--data",
        default=str(PROJECT_DIR / "data" / "clustering" / "documents.csv"),
        help="CSV dataset path.",
    )
    parser.add_argument(
        "--min-documents",
        type=int,
        default=100,
        help="Minimum accepted number of documents.",
    )
    args = parser.parse_args()

    service = ClusteringService()
    report = service.train_from_csv(
        args.data,
        minimum_documents=args.min_documents,
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
