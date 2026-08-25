import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from preprocessing.text_preprocessor import TASK2_DOMAIN_STOPWORDS, TextPreprocessor


class ClusteringVectorizer:
    def __init__(
        self,
        max_features: int = 5000,
        min_df: int = 2,
        max_df: float = 0.95,
    ):
        self.preprocessor = TextPreprocessor(
            extra_stopwords=TASK2_DOMAIN_STOPWORDS,
        )
        self.vectorizer = TfidfVectorizer(
            preprocessor=self.preprocessor.preprocess,
            tokenizer=str.split,
            token_pattern=None,
            lowercase=False,
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=True,
            norm="l2",
        )

    def fit_transform(self, texts: list[str]):
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts: list[str]):
        return self.vectorizer.transform(texts)

    def feature_names(self):
        return self.vectorizer.get_feature_names_out()

    def save(self, path):
        joblib.dump(self.vectorizer, path)

    def load(self, path):
        self.vectorizer = joblib.load(path)
        return self
