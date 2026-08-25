import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_CATEGORIES = {"Economics", "Entertainment", "Politics"}


@dataclass
class ClusteringDocument:
    document_id: str
    text: str
    category: str
    source: str = ""
    url: str = ""


class ClusteringDataLoader:
    def __init__(
        self,
        required_categories=None,
        minimum_documents: int = 100,
    ):
        self.required_categories = set(
            required_categories or REQUIRED_CATEGORIES
        )
        self.minimum_documents = minimum_documents

    def load_csv(self, path: str | Path) -> list[ClusteringDocument]:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        documents = []

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)

            required_columns = {"text", "category"}
            missing = required_columns.difference(reader.fieldnames or [])

            if missing:
                raise ValueError(
                    f"Dataset is missing required columns: {sorted(missing)}"
                )

            for row_number, row in enumerate(reader, start=1):
                text = (row.get("text") or "").strip()
                category = (row.get("category") or "").strip()

                if not text or not category:
                    continue

                document_id = (
                    (row.get("id") or "").strip()
                    or f"doc-{row_number}"
                )

                documents.append(
                    ClusteringDocument(
                        document_id=document_id,
                        text=text,
                        category=category,
                        source=(row.get("source") or "").strip(),
                        url=(row.get("url") or "").strip(),
                    )
                )

        self.validate(documents)
        return documents

    def validate(self, documents: list[ClusteringDocument]):
        if len(documents) < self.minimum_documents:
            raise ValueError(
                f"At least {self.minimum_documents} documents are required. "
                f"Found {len(documents)}."
            )

        categories = {document.category for document in documents}
        missing_categories = self.required_categories.difference(categories)

        if missing_categories:
            raise ValueError(
                "Dataset is missing required categories: "
                f"{sorted(missing_categories)}"
            )

        empty = [
            document.document_id
            for document in documents
            if not document.text.strip()
        ]

        if empty:
            raise ValueError(
                f"Documents with empty text found: {empty[:5]}"
            )

    def category_counts(self, documents: list[ClusteringDocument]) -> dict:
        counts = {}

        for document in documents:
            counts[document.category] = counts.get(document.category, 0) + 1

        return dict(sorted(counts.items()))
