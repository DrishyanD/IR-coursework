from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import BACKEND_DIR, banner, emit_and_save
from clustering.service import ClusteringService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print saved Task 2 dataset/model/evaluation evidence and a live prediction."
    )
    parser.add_argument(
        "--text",
        default=(
            "The central bank raised interest rates after inflation remained "
            "above target and borrowing costs continued to increase."
        ),
        help="New document used for the prediction demonstration.",
    )
    args = parser.parse_args()

    metadata_path = BACKEND_DIR / "saved_models" / "clustering_metadata.json"
    dataset_meta_path = BACKEND_DIR / "data" / "clustering" / "dataset_metadata.json"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    training = metadata.get("training_report", {})
    dataset = training.get("dataset", {})
    evaluation = training.get("evaluation", {})
    cluster_sizes = training.get("cluster_sizes", {})
    cluster_names = training.get("cluster_names", {})
    top_terms = training.get("top_terms", {})

    lines = [
        banner("TASK 2 — CLUSTERING EVIDENCE"),
        f"Documents:       {dataset.get('document_count')}",
        f"Category counts: {dataset.get('category_counts')}",
        f"TF-IDF features: {evaluation.get('feature_count')}",
        f"K-Means clusters:{evaluation.get('cluster_count')}",
        "",
        "Evaluation metrics",
        f"Silhouette (cosine): {evaluation.get('silhouette_cosine')}",
        f"Adjusted Rand Index: {evaluation.get('adjusted_rand_index')}",
        f"NMI:                 {evaluation.get('normalized_mutual_information')}",
        f"Homogeneity:         {evaluation.get('homogeneity')}",
        f"Completeness:        {evaluation.get('completeness')}",
        f"V-measure:           {evaluation.get('v_measure')}",
        "",
        f"Cluster sizes: {cluster_sizes}",
        f"Cluster names: {cluster_names}",
        "",
        "Top terms by cluster",
    ]

    for cluster_id in sorted(top_terms, key=lambda value: int(value)):
        lines.append(
            f"Cluster {cluster_id} ({cluster_names.get(cluster_id, cluster_names.get(str(cluster_id), ''))}): "
            + ", ".join(top_terms[cluster_id])
        )

    if dataset_meta_path.exists():
        dataset_meta = json.loads(dataset_meta_path.read_text(encoding="utf-8"))
        collected = dataset_meta.get("collected_at") or dataset_meta.get("generated_at")
        if collected:
            lines.extend(["", f"Dataset metadata timestamp: {collected}"])

    lines.extend(["", "Live new-document prediction", f"Input: {args.text}"])

    try:
        service = ClusteringService()
        prediction = service.predict(args.text)
        lines.append(json.dumps(prediction, indent=2))
    except Exception as exc:  # evidence should still expose saved metrics if model load fails
        lines.append(f"Prediction could not be run: {type(exc).__name__}: {exc}")

    emit_and_save("04_task2_evidence", lines)


if __name__ == "__main__":
    main()
