"""Coordinates query processing, TF-IDF scoring and result formatting."""

import time

from indexing.boolean_ops import postings_and, postings_or
from models.search_result import SearchResult
from search.cosine_similarity import cosine_similarity
from search.query_processor import QueryProcessor
from search.ranker import Ranker
from search.snippet_generator import SnippetGenerator


class SearchEngine:
    def __init__(self, index_manager, publication_repository):
        self.index_manager = index_manager
        self.publication_repository = publication_repository

        self.query_processor = QueryProcessor(
            preprocessor=index_manager.preprocessor,
            inverted_index=index_manager.inverted_index,
            tfidf=index_manager.tfidf,
        )

        self.ranker = Ranker()
        self.snippet_generator = SnippetGenerator(index_manager.preprocessor)

    def refresh_index_references(self):
        """Point the long-lived query processor at the latest rebuilt indexes."""
        self.query_processor.preprocessor = self.index_manager.preprocessor
        self.query_processor.inverted_index = self.index_manager.inverted_index
        self.query_processor.tfidf = self.index_manager.tfidf

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        """Ranked keyword search using TF-IDF + cosine similarity."""
        if not query or not query.strip():
            return []

        started = time.perf_counter()
        processed = self.query_processor.process(query)

        if not processed["tokens"]:
            return []

        if not processed["candidate_ids"]:
            return []

        if not processed["vector"]:
            return []

        scored = []

        for document_id in processed["candidate_ids"]:
            publication = self.publication_repository.get_by_id(document_id)

            if publication is None:
                continue

            document_vector = self.index_manager.tfidf.document_vector(document_id)

            score = cosine_similarity(
                processed["vector"],
                document_vector,
            )

            # Build a short result snippet from the title and abstract.
            raw_text = " ".join(
                part for part in [publication.title, publication.abstract]
                if part
            )
            snippet = self.snippet_generator.generate(
                raw_text, processed["tokens"]
            )

            scored.append(
                SearchResult(
                    publication=publication,
                    score=score,
                    snippet=snippet,
                )
            )

        results = self.ranker.rank(
            scored_publications=scored,
            top_k=top_k,
            min_score=min_score,
        )

        elapsed_ms = (time.perf_counter() - started) * 1000

        for result in results:
            result.execution_time_ms = round(elapsed_ms, 3)

        return results

    def phrase_search(self, phrase: str, top_k: int = 50) -> list[SearchResult]:
        """Exact phrase search using the positional index.

        Uses ``TextPreprocessor.phrase_tokens()`` which does NOT remove
        stopwords, so stopword removal cannot create false adjacency.
        """
        if not phrase or not phrase.strip():
            return []

        started = time.perf_counter()
        tokens = self.index_manager.preprocessor.phrase_tokens(phrase)

        if not tokens:
            return []

        doc_ids = self.index_manager.positional_index.phrase_search(tokens)

        results = []
        for doc_id in doc_ids[:top_k]:
            publication = self.publication_repository.get_by_id(doc_id)
            if publication is None:
                continue

            raw_text = " ".join(
                part for part in [publication.title, publication.abstract]
                if part
            )
            snippet = self.snippet_generator.generate(raw_text, tokens)

            results.append(
                SearchResult(
                    publication=publication,
                    score=1.0,
                    snippet=snippet,
                )
            )

        elapsed_ms = (time.perf_counter() - started) * 1000
        for result in results:
            result.execution_time_ms = round(elapsed_ms, 3)

        return results

    def boolean_search(
        self, query: str, mode: str = "AND"
    ) -> list[SearchResult]:
        """Boolean search using sorted posting list operations.

        *mode* must be ``"AND"`` or ``"OR"``.  Uses ranked-search
        preprocessing (with stopword removal) for term extraction.
        """
        if not query or not query.strip():
            return []

        started = time.perf_counter()
        tokens = self.index_manager.preprocessor.query_tokens(query)

        if not tokens:
            return []

        # Get one sorted posting list for each query term.
        term_lists = []
        for token in dict.fromkeys(tokens):  # unique, order-preserved
            ids = self.index_manager.inverted_index.sorted_doc_ids(token)
            term_lists.append(ids)

        if not term_lists:
            return []

        if mode.upper() == "AND":
            result_ids = term_lists[0]
            for lst in term_lists[1:]:
                result_ids = postings_and(result_ids, lst)
        else:
            result_ids = term_lists[0]
            for lst in term_lists[1:]:
                result_ids = postings_or(result_ids, lst)

        results = []
        for doc_id in result_ids:
            publication = self.publication_repository.get_by_id(doc_id)
            if publication is not None:
                results.append(
                    SearchResult(publication=publication, score=1.0)
                )

        elapsed_ms = (time.perf_counter() - started) * 1000
        for result in results:
            result.execution_time_ms = round(elapsed_ms, 3)

        return results

    def proximity_search(
        self, term1: str, term2: str, distance: int = 5, top_k: int = 50,
    ) -> list[SearchResult]:
        """NEAR-k proximity search using the positional index.

        Returns documents where *term1* and *term2* appear within
        *distance* words of each other.
        """
        if not term1 or not term2:
            return []

        started = time.perf_counter()
        tokens1 = self.index_manager.preprocessor.phrase_tokens(term1)
        tokens2 = self.index_manager.preprocessor.phrase_tokens(term2)

        if not tokens1 or not tokens2:
            return []

        stemmed_a = tokens1[0]
        stemmed_b = tokens2[0]

        doc_ids = self.index_manager.positional_index.near_search(
            stemmed_a, stemmed_b, distance
        )

        results = []
        for doc_id in doc_ids[:top_k]:
            publication = self.publication_repository.get_by_id(doc_id)
            if publication is None:
                continue

            raw_text = " ".join(
                part for part in [publication.title, publication.abstract]
                if part
            )
            snippet = self.snippet_generator.generate(
                raw_text, [stemmed_a, stemmed_b]
            )

            results.append(
                SearchResult(
                    publication=publication,
                    score=1.0,
                    snippet=snippet,
                )
            )

        elapsed_ms = (time.perf_counter() - started) * 1000
        for result in results:
            result.execution_time_ms = round(elapsed_ms, 3)

        return results

    def explain_query(self, query: str) -> dict:
        processed = self.query_processor.process(query)

        return {
            "query": processed["query"],
            "tokens": processed["tokens"],
            "candidate_ids": sorted(processed["candidate_ids"]),
            "query_vector": processed["vector"],
        }
