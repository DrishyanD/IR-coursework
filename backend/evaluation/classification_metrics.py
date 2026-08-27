"""Basic classification-style metrics used by the clustering evidence helpers."""

"""Simple confusion matrix and per-class Precision/Recall/F1/Accuracy.

Pure Python — no sklearn dependency. Works alongside the existing
ClusteringEvaluator which uses sklearn for ARI, NMI, Silhouette, etc.

Designed for evaluating clustering results when cluster labels have been
mapped to known categories (post-hoc evaluation only — known labels are
never used as input features).
"""


def confusion_matrix(
    true_labels: list[str],
    predicted_labels: list[str],
    label_order: list[str] | None = None,
) -> dict:
    """Compute a multi-class confusion matrix with per-class metrics.

    Parameters
    ----------
    true_labels : list[str]
        Ground-truth category labels.
    predicted_labels : list[str]
        Predicted (or cluster-mapped) labels, same length as *true_labels*.
    label_order : list[str] | None
        Optional fixed ordering of labels.  If ``None``, labels are sorted
        alphabetically.

    Returns
    -------
    dict
        ``matrix`` (list of lists), ``labels``, per-class TP/FP/FN/TN/P/R/F1,
        macro averages, and overall accuracy.
    """
    if len(true_labels) != len(predicted_labels):
        raise ValueError(
            f"Length mismatch: {len(true_labels)} true vs "
            f"{len(predicted_labels)} predicted."
        )

    if not true_labels:
        return {
            "matrix": [],
            "labels": [],
            "per_class": {},
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "overall_accuracy": 0.0,
        }

    labels = label_order or sorted(set(true_labels) | set(predicted_labels))
    label_to_idx = {label: i for i, label in enumerate(labels)}
    n = len(labels)

    # Build the confusion matrix.
    matrix = [[0] * n for _ in range(n)]
    for true, pred in zip(true_labels, predicted_labels):
        i = label_to_idx.get(true)
        j = label_to_idx.get(pred)
        if i is not None and j is not None:
            matrix[i][j] += 1

    total = len(true_labels)

    # Calculate precision, recall and F1 for each class.
    per_class = {}
    for idx, label in enumerate(labels):
        tp = matrix[idx][idx]
        fp = sum(matrix[row][idx] for row in range(n)) - tp
        fn = sum(matrix[idx][col] for col in range(n)) - tp
        tn = total - tp - fp - fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        accuracy = (tp + tn) / total if total > 0 else 0.0

        per_class[label] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "accuracy": round(accuracy, 6),
        }

    # Macro averages give each class equal weight.
    macro_precision = sum(c["precision"] for c in per_class.values()) / n
    macro_recall = sum(c["recall"] for c in per_class.values()) / n
    macro_f1 = sum(c["f1"] for c in per_class.values()) / n

    # Accuracy is the fraction of all correctly assigned items.
    correct = sum(matrix[i][i] for i in range(n))
    overall_accuracy = correct / total if total > 0 else 0.0

    return {
        "matrix": matrix,
        "labels": labels,
        "per_class": per_class,
        "macro_precision": round(macro_precision, 6),
        "macro_recall": round(macro_recall, 6),
        "macro_f1": round(macro_f1, 6),
        "overall_accuracy": round(overall_accuracy, 6),
    }
