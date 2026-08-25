"""Builds, saves and reloads the vocabulary, inverted index and positional index."""

import json
from pathlib import Path

from config import PROJECT_DIR
from indexing.inverted_index import InvertedIndex
from indexing.positional_index import PositionalIndex
from indexing.tfidf import TFIDF
from indexing.vocabulary import Vocabulary
from preprocessing.text_preprocessor import TASK1_DOMAIN_STOPWORDS, TextPreprocessor


class IndexManager:
    def __init__(self, index_dir: str | Path | None = None):
        self.index_dir = Path(index_dir or (PROJECT_DIR / "data" / "indexes"))
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.vocabulary = Vocabulary()
        self.inverted_index = InvertedIndex()
        self.positional_index = PositionalIndex()
        self.tfidf = TFIDF(self.inverted_index)
        self.preprocessor = TextPreprocessor(
            extra_stopwords=TASK1_DOMAIN_STOPWORDS,
        )

    def build_from_publications(self, publications):
        documents = {}
        positional_documents = {}

        for publication in publications:
            if publication.id is None:
                raise ValueError(
                    "Each publication must have a database ID before indexing."
                )

            author_names = [author.name for author in publication.authors]

            # Ranked search removes stopwords to keep the TF-IDF vocabulary focused.
            tokens = self.preprocessor.preprocess_fields(
                title=publication.title,
                authors=author_names,
                abstract=publication.abstract,
                keywords=publication.keywords,
            )

            # Phrase search keeps stopwords so word positions stay accurate.
            pos_tokens = self.preprocessor.preprocess_fields_with_positions(
                title=publication.title,
                authors=author_names,
                abstract=publication.abstract,
                keywords=publication.keywords,
            )

            documents[int(publication.id)] = tokens
            positional_documents[int(publication.id)] = pos_tokens

        self.vocabulary = Vocabulary()
        self.vocabulary.build(documents)

        self.inverted_index = InvertedIndex()
        self.inverted_index.build(documents)

        self.positional_index = PositionalIndex()
        self.positional_index.build(positional_documents)

        self.tfidf = TFIDF(self.inverted_index)

        return documents

    def save(self):
        vocabulary_path = self.index_dir / "vocabulary.json"
        index_path = self.index_dir / "inverted_index.json"
        positional_path = self.index_dir / "positional_index.json"

        vocabulary_path.write_text(
            json.dumps(self.vocabulary.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        index_path.write_text(
            json.dumps(self.inverted_index.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        positional_path.write_text(
            json.dumps(self.positional_index.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self):
        vocabulary_path = self.index_dir / "vocabulary.json"
        index_path = self.index_dir / "inverted_index.json"
        positional_path = self.index_dir / "positional_index.json"

        if not vocabulary_path.exists() or not index_path.exists():
            raise FileNotFoundError(
                "Saved index files were not found. Build and save the index first."
            )

        vocabulary_data = json.loads(vocabulary_path.read_text(encoding="utf-8"))
        index_data = json.loads(index_path.read_text(encoding="utf-8"))

        self.vocabulary = Vocabulary.from_dict(vocabulary_data)
        self.inverted_index = InvertedIndex.from_dict(index_data)
        self.tfidf = TFIDF(self.inverted_index)

        if positional_path.exists():
            positional_data = json.loads(
                positional_path.read_text(encoding="utf-8")
            )
            self.positional_index = PositionalIndex.from_dict(positional_data)
        else:
            self.positional_index = PositionalIndex()

    def stats(self):
        return {
            "documents": self.inverted_index.document_count,
            "vocabulary_size": len(self.vocabulary),
            "terms_with_postings": len(self.inverted_index.postings),
            "positional_index_terms": len(self.positional_index.positions),
            "sorted_postings": True,
        }
