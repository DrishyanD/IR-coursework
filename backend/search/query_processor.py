class QueryProcessor:
    def __init__(self, preprocessor, inverted_index, tfidf):
        self.preprocessor = preprocessor
        self.inverted_index = inverted_index
        self.tfidf = tfidf

    def process(self, query: str):
        tokens = self.preprocessor.query_tokens(query)

        if not tokens:
            return {
                "query": query,
                "tokens": [],
                "candidate_ids": set(),
                "vector": {},
            }

        candidate_ids = self.inverted_index.candidate_documents(tokens)
        vector = self.tfidf.query_vector(tokens)

        return {
            "query": query,
            "tokens": tokens,
            "candidate_ids": candidate_ids,
            "vector": vector,
        }
