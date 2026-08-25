import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import json
from collections import Counter

from config import PROJECT_DIR


def main():
    dataset_csv = PROJECT_DIR / "data" / "clustering" / "documents.csv"
    metadata_json = PROJECT_DIR / "data" / "clustering" / "dataset_metadata.json"

    if not dataset_csv.exists():
        print(f"Dataset not found at {dataset_csv}")
        return

    docs = []
    with dataset_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            docs.append(row)

    print(f"Total documents: {len(docs)}")

    category_counts = Counter(d["category"] for d in docs)
    print("\nCategory Distribution:")
    for cat, count in category_counts.most_common():
        print(f"  {cat}: {count} ({count/len(docs)*100:.1f}%)")

    lengths = [len(d["text"].split()) for d in docs]
    print("\nText Lengths (words):")
    print(f"  Min: {min(lengths)}")
    print(f"  Max: {max(lengths)}")
    print(f"  Avg: {sum(lengths)/len(lengths):.1f}")


    mojibake_markers = ("Â", "â\x80", "Ã")
    mojibake_rows = sum(
        1 for document in docs
        if any(marker in document.get("text", "") for marker in mojibake_markers)
    )
    if mojibake_rows:
        print(f"\nEncoding warning: {mojibake_rows} rows contain legacy mojibake markers.")
        print("Re-collect with the current byte-aware BBC parser before final retraining.")

    if metadata_json.exists():
        metadata = json.loads(metadata_json.read_text(encoding="utf-8"))
        print("\nMetadata:")
        print(f"  Source Feeds: {len(metadata.get('feeds', []))}")
        print(f"  Timestamp: {metadata.get('collected_at', 'unknown')}")

    print("\n(Run complete)")


if __name__ == "__main__":
    main()
