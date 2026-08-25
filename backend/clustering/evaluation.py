from sklearn.metrics import (
    adjusted_rand_score,
    completeness_score,
    homogeneity_score,
    normalized_mutual_info_score,
    silhouette_score,
    v_measure_score,
)


class ClusteringEvaluator:
    def evaluate(self, matrix, predicted_labels, true_categories):
        unique_clusters = len(set(int(label) for label in predicted_labels))

        if unique_clusters > 1 and matrix.shape[0] > unique_clusters:
            silhouette = float(
                silhouette_score(
                    matrix,
                    predicted_labels,
                    metric="cosine",
                )
            )
        else:
            silhouette = 0.0

        return {
            "document_count": int(matrix.shape[0]),
            "feature_count": int(matrix.shape[1]),
            "cluster_count": unique_clusters,
            "silhouette_cosine": silhouette,
            "adjusted_rand_index": float(
                adjusted_rand_score(
                    true_categories,
                    predicted_labels,
                )
            ),
            "normalized_mutual_information": float(
                normalized_mutual_info_score(
                    true_categories,
                    predicted_labels,
                )
            ),
            "homogeneity": float(
                homogeneity_score(
                    true_categories,
                    predicted_labels,
                )
            ),
            "completeness": float(
                completeness_score(
                    true_categories,
                    predicted_labels,
                )
            ),
            "v_measure": float(
                v_measure_score(
                    true_categories,
                    predicted_labels,
                )
            ),
        }
