class ClusterPredictor:
    def __init__(
        self,
        vectorizer,
        model,
        cluster_name_map: dict[int, str] | None = None,
    ):
        self.vectorizer = vectorizer
        self.model = model
        self.cluster_name_map = cluster_name_map or {}

    def predict(self, text: str) -> dict:
        if not text or not text.strip():
            raise ValueError("Document text cannot be empty.")

        matrix = self.vectorizer.transform([text])
        cluster_id = int(self.model.predict(matrix)[0])

        distances = self.model.transform(matrix)[0]
        distance = float(distances[cluster_id])

        other_distances = [
            float(value)
            for index, value in enumerate(distances)
            if index != cluster_id
        ]
        second_nearest = min(other_distances) if other_distances else distance
        if second_nearest > 0:
            separation_margin = max(0.0, min(1.0, (second_nearest - distance) / second_nearest))
        else:
            separation_margin = 0.0

        return {
            "cluster_id": cluster_id,
            "predicted_category": self.cluster_name_map.get(
                cluster_id,
                f"Cluster {cluster_id}",
            ),
            "distance_to_centroid": distance,
            "second_nearest_distance": second_nearest,
            "separation_margin": separation_margin,
        }
