"""TF-IDF weighting using the taught log₁₀ formulas.

Term Frequency (TF):
    TF(t, d) = 1 + log₁₀(tf)    if tf > 0
    TF(t, d) = 0                 if tf = 0

Inverse Document Frequency (IDF):
    IDF(t) = log₁₀(N / df)      where N = total documents, df = document frequency

Both document and query TF-IDF vectors are L2-normalised so that cosine
similarity reduces to a simple dot product of unit vectors.

References:
    - Introduction to Information Retrieval (Manning, Raghavan, Schütze), §6.2
    - Coursework brief: "custom TF-IDF implementation"
"""

import math
from collections import Counter


class TFIDF:
    def __init__(self, inverted_index):
        self.inverted_index = inverted_index
        self.idf_cache = {}

    def tf(self, term_frequency: int) -> float:
        """Logarithmic term frequency: 1 + log₁₀(tf).

        Returns 0.0 for zero or negative raw frequencies.
        """
        if term_frequency <= 0:
            return 0.0

        return 1.0 + math.log10(term_frequency)

    def idf(self, term: str) -> float:
        """Inverse document frequency: log₁₀(N / df).

        Returns 0.0 if the term does not appear in any document or
        if the corpus is empty.  Results are cached per term.
        """
        if term in self.idf_cache:
            return self.idf_cache[term]

        total_documents = self.inverted_index.document_count
        document_frequency = self.inverted_index.document_frequency(term)

        if total_documents == 0 or document_frequency == 0:
            value = 0.0
        else:
            value = math.log10(total_documents / document_frequency)

        self.idf_cache[term] = value
        return value

    def document_vector(self, document_id: int) -> dict[str, float]:
        """Build an L2-normalised TF-IDF vector for *document_id*."""
        vector = {}

        for term, postings in self.inverted_index.postings.items():
            frequency = postings.get(document_id)

            if frequency is None:
                continue

            weight = self.tf(frequency) * self.idf(term)

            if weight > 0:
                vector[term] = weight

        return self._normalize(vector)

    def query_vector(self, query_tokens: list[str]) -> dict[str, float]:
        """Build an L2-normalised TF-IDF vector for *query_tokens*."""
        counts = Counter(query_tokens)
        vector = {}

        for term, frequency in counts.items():
            weight = self.tf(frequency) * self.idf(term)

            if weight > 0:
                vector[term] = weight

        return self._normalize(vector)

    def _normalize(self, vector: dict[str, float]) -> dict[str, float]:
        """L2-normalise *vector* so that its Euclidean length is 1.0.

        After normalisation, the dot product of two such vectors equals
        their cosine similarity (no separate denominator needed).
        """
        magnitude = math.sqrt(sum(weight * weight for weight in vector.values()))

        if magnitude == 0:
            return {}

        return {
            term: weight / magnitude
            for term, weight in vector.items()
        }
