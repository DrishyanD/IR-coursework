import joblib
from sklearn.cluster import KMeans


class KMeansClusteringModel:
    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42,
        n_init: int = 20,
    ):
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=n_init,
        )

    def fit(self, matrix):
        self.model.fit(matrix)
        return self

    def fit_predict(self, matrix):
        return self.model.fit_predict(matrix)

    def predict(self, matrix):
        return self.model.predict(matrix)

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)
        return self
