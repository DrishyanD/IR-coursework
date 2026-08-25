"""Trains, saves, loads and uses the Task 2 TF-IDF/K-Means model."""

import json
from pathlib import Path

from config import PROJECT_DIR
from clustering.cluster_analyzer import ClusterAnalyzer
from clustering.data_loader import ClusteringDataLoader
from clustering.evaluation import ClusteringEvaluator
from clustering.kmeans_model import KMeansClusteringModel
from clustering.predictor import ClusterPredictor
from clustering.vectorizer import ClusteringVectorizer


class ClusteringService:
    def __init__(
        self,
        model_dir: str | Path | None = None,
    ):
        self.model_dir = Path(
            model_dir or (PROJECT_DIR / "saved_models")
        )
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.vectorizer = ClusteringVectorizer()
        self.model = KMeansClusteringModel(n_clusters=3)
        self.analyzer = ClusterAnalyzer()
        self.evaluator = ClusteringEvaluator()
        self.cluster_name_map = {}
        self.loaded = False

    @property
    def model_path(self):
        return self.model_dir / "kmeans.pkl"

    @property
    def vectorizer_path(self):
        return self.model_dir / "clustering_vectorizer.pkl"

    @property
    def metadata_path(self):
        return self.model_dir / "clustering_metadata.json"

    def train_from_csv(
        self,
        csv_path,
        minimum_documents: int = 100,
    ) -> dict:
        loader = ClusteringDataLoader(
            minimum_documents=minimum_documents
        )
        documents = loader.load_csv(csv_path)

        texts = [document.text for document in documents]
        true_categories = [document.category for document in documents]

        matrix = self.vectorizer.fit_transform(texts)
        labels = self.model.fit_predict(matrix)

        feature_names = self.vectorizer.feature_names()
        self.cluster_name_map = self.analyzer.infer_cluster_names(
            labels,
            true_categories,
        )

        report = {
            "dataset": {
                "document_count": len(documents),
                "category_counts": loader.category_counts(documents),
            },
            "evaluation": self.evaluator.evaluate(
                matrix,
                labels,
                true_categories,
            ),
            "cluster_sizes": self.analyzer.cluster_sizes(labels),
            "cluster_composition": self.analyzer.category_composition(
                labels,
                true_categories,
            ),
            "cluster_names": self.cluster_name_map,
            "top_terms": self.analyzer.top_terms(
                self.model.model,
                feature_names,
                top_n=10,
            ),
        }

        self.save(report)
        self.loaded = True

        return report

    def save(self, report: dict):
        self.vectorizer.save(self.vectorizer_path)
        self.model.save(self.model_path)

        metadata = {
            "cluster_name_map": {
                str(key): value
                for key, value in self.cluster_name_map.items()
            },
            "training_report": report,
        }

        self.metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self):
        if not (
            self.model_path.exists()
            and self.vectorizer_path.exists()
            and self.metadata_path.exists()
        ):
            raise FileNotFoundError(
                "Saved clustering model artifacts were not found."
            )

        self.vectorizer.load(self.vectorizer_path)
        self.model.load(self.model_path)

        metadata = json.loads(
            self.metadata_path.read_text(encoding="utf-8")
        )

        self.cluster_name_map = {
            int(key): value
            for key, value in metadata.get(
                "cluster_name_map",
                {},
            ).items()
        }

        self.loaded = True
        return metadata

    def predict(self, text: str) -> dict:
        if not self.loaded:
            self.load()

        predictor = ClusterPredictor(
            self.vectorizer.vectorizer,
            self.model.model,
            self.cluster_name_map,
        )

        return predictor.predict(text)

    def status(self):
        return {
            "trained": (
                self.model_path.exists()
                and self.vectorizer_path.exists()
                and self.metadata_path.exists()
            ),
            "model_path": str(self.model_path),
            "vectorizer_path": str(self.vectorizer_path),
            "metadata_path": str(self.metadata_path),
        }

    def evidence(self):
        if not self.metadata_path.exists():
            raise FileNotFoundError("Saved clustering metadata was not found.")

        model_metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        dataset_path = PROJECT_DIR / "data" / "clustering" / "dataset_metadata.json"
        dataset_metadata = (
            json.loads(dataset_path.read_text(encoding="utf-8"))
            if dataset_path.exists()
            else {}
        )
        return {
            "trained": self.status()["trained"],
            "dataset_metadata": dataset_metadata,
            "training_report": model_metadata.get("training_report", {}),
        }
