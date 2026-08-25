"""Small inverted index that stores term frequencies for each document."""

from collections import Counter, defaultdict


class InvertedIndex:
    def __init__(self):
        self.postings = defaultdict(dict)
        self.document_lengths = {}
        self.document_count = 0

    def build(self, documents: dict[int, list[str]]):
        self.postings.clear()
        self.document_lengths.clear()
        self.document_count = len(documents)

        for document_id, tokens in documents.items():
            counts = Counter(tokens)
            self.document_lengths[document_id] = len(tokens)

            for term, frequency in counts.items():
                self.postings[term][document_id] = frequency

    def add_document(self, document_id: int, tokens: list[str]):
        if document_id in self.document_lengths:
            self.remove_document(document_id)

        counts = Counter(tokens)
        self.document_lengths[document_id] = len(tokens)

        for term, frequency in counts.items():
            self.postings[term][document_id] = frequency

        self.document_count = len(self.document_lengths)

    def remove_document(self, document_id: int):
        for term in list(self.postings.keys()):
            self.postings[term].pop(document_id, None)

            if not self.postings[term]:
                del self.postings[term]

        self.document_lengths.pop(document_id, None)
        self.document_count = len(self.document_lengths)

    def get_postings(self, term: str) -> dict[int, int]:
        return dict(self.postings.get(term, {}))

    def sorted_postings(self, term: str) -> list[tuple[int, int]]:
        """Return posting list for *term* as ``[(doc_id, freq), ...]``
        sorted by doc_id ascending.  Used by Boolean merge operations."""
        return sorted(self.postings.get(term, {}).items())

    def sorted_doc_ids(self, term: str) -> list[int]:
        """Return document IDs containing *term*, sorted ascending."""
        return sorted(self.postings.get(term, {}).keys())

    def all_doc_ids_sorted(self) -> list[int]:
        """Return all indexed document IDs, sorted ascending."""
        return sorted(self.document_lengths.keys())

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, {}))

    def candidate_documents(self, terms: list[str]) -> set[int]:
        candidates = set()

        for term in terms:
            candidates.update(self.postings.get(term, {}).keys())

        return candidates

    def to_dict(self):
        return {
            "postings": {
                term: {str(doc_id): frequency for doc_id, frequency in docs.items()}
                for term, docs in self.postings.items()
            },
            "document_lengths": {
                str(doc_id): length
                for doc_id, length in self.document_lengths.items()
            },
            "document_count": self.document_count,
        }

    @classmethod
    def from_dict(cls, data):
        index = cls()
        index.postings = defaultdict(dict)

        for term, docs in data.get("postings", {}).items():
            index.postings[term] = {
                int(doc_id): int(frequency)
                for doc_id, frequency in docs.items()
            }

        index.document_lengths = {
            int(doc_id): int(length)
            for doc_id, length in data.get("document_lengths", {}).items()
        }
        index.document_count = int(data.get("document_count", 0))
        return index
