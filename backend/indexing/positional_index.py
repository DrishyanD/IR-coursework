"""Positional index used for exact phrase and NEAR-k searches."""

from collections import defaultdict


class PositionalIndex:
    def __init__(self):
        # Each term maps to document IDs and the positions where the term appears.
        self.positions: dict[str, dict[int, list[int]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.document_count = 0

    def build(self, documents: dict[int, list[tuple[str, int]]]):
        """Build from ``{doc_id: [(stemmed_token, position), ...], ...}``.

        The input must come from ``TextPreprocessor.tokenize_with_positions``
        or ``preprocess_fields_with_positions``.
        """
        self.positions.clear()
        self.document_count = len(documents)

        for doc_id, token_positions in documents.items():
            for token, position in token_positions:
                self.positions[token][doc_id].append(position)

        # Sorted positions make phrase and proximity checks predictable.
        for term_docs in self.positions.values():
            for doc_id in term_docs:
                term_docs[doc_id].sort()

    def get_positions(self, term: str, doc_id: int) -> list[int]:
        """Return sorted positions of *term* in *doc_id*, or ``[]``."""
        return list(self.positions.get(term, {}).get(doc_id, []))

    def phrase_search(self, phrase_tokens: list[str]) -> list[int]:
        """Return sorted doc IDs where *phrase_tokens* appear consecutively.

        Uses the positional index to verify that each successive token
        appears exactly one position after the previous one.

        *phrase_tokens* must come from ``TextPreprocessor.phrase_tokens()``
        which does NOT remove stopwords, so position gaps from stopword
        removal cannot create false adjacency.
        """
        if not phrase_tokens:
            return []

        if len(phrase_tokens) == 1:
            return sorted(self.positions.get(phrase_tokens[0], {}).keys())

        # Start with documents that contain the first term.
        first_term = phrase_tokens[0]
        if first_term not in self.positions:
            return []

        candidate_docs = set(self.positions[first_term].keys())

        # Only documents containing every phrase term can match.
        for token in phrase_tokens[1:]:
            if token not in self.positions:
                return []
            candidate_docs &= set(self.positions[token].keys())

        if not candidate_docs:
            return []

        # Check whether the terms appear next to each other in the right order.
        result = []
        for doc_id in sorted(candidate_docs):
            first_positions = self.positions[first_term][doc_id]

            for start_pos in first_positions:
                found = True
                expected_pos = start_pos

                for i, token in enumerate(phrase_tokens):
                    if i == 0:
                        continue
                    expected_pos += 1
                    token_positions = self.positions[token][doc_id]
                    if expected_pos not in token_positions:
                        found = False
                        break

                if found:
                    result.append(doc_id)
                    break  # One phrase match is enough to keep the document.

        return result

    def near_search(self, term_a: str, term_b: str, k: int) -> list[int]:
        """Return sorted doc IDs where *term_a* and *term_b* appear within
        *k* positions of each other.
        """
        if term_a not in self.positions or term_b not in self.positions:
            return []

        docs_a = set(self.positions[term_a].keys())
        docs_b = set(self.positions[term_b].keys())
        candidate_docs = docs_a & docs_b

        result = []
        for doc_id in sorted(candidate_docs):
            positions_a = self.positions[term_a][doc_id]
            positions_b = self.positions[term_b][doc_id]

            # Two pointers find a close pair without comparing every position.
            i, j = 0, 0
            found = False
            while i < len(positions_a) and j < len(positions_b):
                diff = abs(positions_a[i] - positions_b[j])
                if diff <= k:
                    found = True
                    break
                if positions_a[i] < positions_b[j]:
                    i += 1
                else:
                    j += 1

            if found:
                result.append(doc_id)

        return result

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "positions": {
                term: {
                    str(doc_id): pos_list
                    for doc_id, pos_list in docs.items()
                }
                for term, docs in self.positions.items()
            },
            "document_count": self.document_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PositionalIndex":
        """Deserialize from a dict produced by :meth:`to_dict`."""
        index = cls()
        index.document_count = int(data.get("document_count", 0))

        for term, docs in data.get("positions", {}).items():
            for doc_id_str, pos_list in docs.items():
                index.positions[term][int(doc_id_str)] = [
                    int(p) for p in pos_list
                ]

        return index
