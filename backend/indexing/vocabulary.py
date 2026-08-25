class Vocabulary:
    def __init__(self):
        self.term_to_id = {}
        self.id_to_term = {}

    def add(self, term: str) -> int:
        if term in self.term_to_id:
            return self.term_to_id[term]

        term_id = len(self.term_to_id)
        self.term_to_id[term] = term_id
        self.id_to_term[term_id] = term
        return term_id

    def build(self, documents: dict[int, list[str]]):
        for tokens in documents.values():
            for term in tokens:
                self.add(term)

    def get_id(self, term: str) -> int | None:
        return self.term_to_id.get(term)

    def get_term(self, term_id: int) -> str | None:
        return self.id_to_term.get(term_id)

    def __len__(self):
        return len(self.term_to_id)

    def to_dict(self):
        return {
            "term_to_id": self.term_to_id,
            "id_to_term": self.id_to_term,
        }

    @classmethod
    def from_dict(cls, data):
        vocabulary = cls()
        vocabulary.term_to_id = {
            str(term): int(term_id)
            for term, term_id in data.get("term_to_id", {}).items()
        }
        vocabulary.id_to_term = {
            int(term_id): str(term)
            for term_id, term in data.get("id_to_term", {}).items()
        }
        return vocabulary
