"""Shared text cleaning for indexed publications, queries and phrase-search positions."""

import re
import unicodedata

from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


TASK1_DOMAIN_STOPWORDS = {
    "author",
    "authors",
    "coventry",
    "publication",
    "publications",
    "published",
    "pureportal",
    "university",
}

TASK2_DOMAIN_STOPWORDS = {
    "according",
    "bbc",
    "latest",
    "news",
    "new",
    "people",
    "report",
    "reported",
    "said",
    "say",
    "says",
    "told",
    "year",
}


class TextPreprocessor:
    def __init__(
        self,
        remove_stopwords: bool = True,
        use_stemming: bool = True,
        min_token_length: int = 2,
        extra_stopwords: set[str] | None = None,
    ):
        self.remove_stopwords = remove_stopwords
        self.use_stemming = use_stemming
        self.min_token_length = min_token_length
        self.stopwords = set(ENGLISH_STOP_WORDS)
        self.stopwords.update(
            word.casefold().strip()
            for word in (extra_stopwords or set())
            if word.strip()
        )
        self.stemmer = SnowballStemmer("english")
        # Store stemmed stopwords too, so words such as "years" cannot come back after stemming.
        self.stopword_stems = {
            self.stemmer.stem(word) for word in self.stopwords if word
        }

    def normalize(self, text: str | None) -> str:
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)
        text = text.lower()
        text = text.replace("’", "'")
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"[^a-z0-9\s'-]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def tokenize(self, text: str | None) -> list[str]:
        normalized = self.normalize(text)

        if not normalized:
            return []

        # Keep both forms of a hyphenated word, for example "well-being" and "wellbeing".
        raw_tokens = re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", normalized)
        tokens = []

        for raw_token in raw_tokens:
            if "-" in raw_token:
                parts = [part for part in raw_token.split("-") if part]
                if len(parts) > 1:
                    tokens.append("".join(parts))
                    tokens.extend(parts)
            else:
                tokens.append(raw_token)

        cleaned = []

        for token in tokens:
            token = token.strip("'")

            if len(token) < self.min_token_length:
                continue

            if self.remove_stopwords and token in self.stopwords:
                continue

            if self.use_stemming:
                token = self.stemmer.stem(token)
                if self.remove_stopwords:
                    # Build this set lazily so older saved objects can still be loaded.
                    stopword_stems = getattr(self, "stopword_stems", None)
                    if stopword_stems is None:
                        stopword_stems = {
                            self.stemmer.stem(word)
                            for word in self.stopwords
                            if word
                        }
                        self.stopword_stems = stopword_stems
                    if token in stopword_stems:
                        continue

            if token:
                cleaned.append(token)

        return cleaned

    def preprocess(self, text: str | None) -> str:
        return " ".join(self.tokenize(text))

    def preprocess_fields(
        self,
        title: str | None = None,
        authors: list[str] | None = None,
        abstract: str | None = None,
        keywords: list[str] | None = None,
    ) -> list[str]:
        parts = []

        if title:
            parts.append(title)

        if authors:
            parts.extend(authors)

        if abstract:
            parts.append(abstract)

        if keywords:
            parts.extend(keywords)

        return self.tokenize(" ".join(parts))

    def query_tokens(self, query: str | None) -> list[str]:
        return self.tokenize(query)

    def tokenize_with_positions(self, text: str | None) -> list[tuple[str, int]]:
        # Keep stopwords here because removing them would create false phrase positions.
        normalized = self.normalize(text)
        if not normalized:
            return []

        raw_tokens = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", normalized)
        result = []

        for position, token in enumerate(raw_tokens):
            token = token.strip("'")
            if len(token) < self.min_token_length:
                continue

            if self.use_stemming:
                token = self.stemmer.stem(token)

            if token:
                result.append((token, position))

        return result

    def phrase_tokens(self, phrase: str | None) -> list[str]:
        # Phrase queries use the same position-safe tokenisation.
        normalized = self.normalize(phrase)
        if not normalized:
            return []

        raw_tokens = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", normalized)
        result = []

        for token in raw_tokens:
            token = token.strip("'")
            if len(token) < self.min_token_length:
                continue

            if self.use_stemming:
                token = self.stemmer.stem(token)

            if token:
                result.append(token)

        return result

    def preprocess_fields_with_positions(
        self,
        title: str | None = None,
        authors: list[str] | None = None,
        abstract: str | None = None,
        keywords: list[str] | None = None,
    ) -> list[tuple[str, int]]:
        """Like :meth:`preprocess_fields` but returns position-tagged tokens.

        Positions are contiguous across all concatenated fields.
        Stopwords are NOT removed (positions must be preserved).
        """
        parts = []
        if title:
            parts.append(title)
        if authors:
            parts.extend(authors)
        if abstract:
            parts.append(abstract)
        if keywords:
            parts.extend(keywords)

        return self.tokenize_with_positions(" ".join(parts))
