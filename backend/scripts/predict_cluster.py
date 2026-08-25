import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clustering.service import ClusteringService


def main():
    parser = argparse.ArgumentParser(
        description="Assign a new document to a trained Task 2 cluster."
    )
    parser.add_argument(
        "text",
        help="New document or sentence to classify into a cluster.",
    )
    args = parser.parse_args()

    service = ClusteringService()
    result = service.predict(args.text)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
