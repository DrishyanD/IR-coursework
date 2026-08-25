"""Summarises learned clusters and gives them readable topic labels after training."""

from collections import Counter, defaultdict
from itertools import permutations


class ClusterAnalyzer:
    def top_terms(
        self,
        model,
        feature_names,
        top_n: int = 10,
    ) -> dict[int, list[str]]:
        result = {}

        for cluster_id, centroid in enumerate(model.cluster_centers_):
            top_indices = centroid.argsort()[::-1][:top_n]
            result[int(cluster_id)] = [
                str(feature_names[index])
                for index in top_indices
            ]

        return result

    def cluster_sizes(self, labels) -> dict[int, int]:
        counts = Counter(int(label) for label in labels)
        return dict(sorted(counts.items()))

    def category_composition(
        self,
        labels,
        true_categories: list[str],
    ) -> dict[int, dict[str, int]]:
        composition = defaultdict(Counter)

        for cluster_id, category in zip(labels, true_categories):
            composition[int(cluster_id)][category] += 1

        return {
            cluster_id: dict(counter)
            for cluster_id, counter in sorted(composition.items())
        }

    def infer_cluster_names(
        self,
        labels,
        true_categories: list[str],
    ) -> dict[int, str]:
        composition = self.category_composition(labels, true_categories)
        cluster_ids = sorted(composition)
        categories = sorted(set(true_categories))

        if len(cluster_ids) != len(categories):
            return {
                cluster_id: max(counts.items(), key=lambda item: (item[1], item[0]))[0]
                if counts else f"Cluster {cluster_id}"
                for cluster_id, counts in composition.items()
            }

        # Give each known category to one cluster so an imbalanced dataset cannot reuse the same label everywhere.
        best_categories = max(
            permutations(categories),
            key=lambda assignment: sum(
                composition[cluster_id].get(category, 0)
                for cluster_id, category in zip(cluster_ids, assignment)
            ),
        )
        return dict(zip(cluster_ids, best_categories))
