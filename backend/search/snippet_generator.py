"""Builds a short search-result snippet around the most useful query matches."""

import re

from preprocessing.text_preprocessor import TextPreprocessor


class SnippetGenerator:
    def __init__(self, preprocessor: TextPreprocessor | None = None):
        self.preprocessor = preprocessor or TextPreprocessor()

    def generate(
        self,
        text: str | None,
        query_tokens: list[str],
        max_length: int = 200,
    ) -> str:
        """Extract a snippet from *text* highlighting *query_tokens*.

        Returns the best window of up to *max_length* characters, or ""
        if no text is provided.
        """
        if not text or not query_tokens:
            return ""

        text = text.strip()
        if len(text) <= max_length:
            return text

        # Match stems so the snippet uses the same word forms as search.
        normalized = self.preprocessor.normalize(text)
        if not normalized:
            return text[:max_length] + "..."

        # Work with the original words so the final snippet still reads naturally.
        words = re.findall(r"\S+", text)
        if not words:
            return ""

        # Give matching words a simple score of 1.
        query_set = set(query_tokens)
        word_scores = []
        for i, word in enumerate(words):
            # Normalise and stem each word before comparing it with the query.
            clean = re.sub(r"[^a-z0-9']", "", word.lower()).strip("'")
            if len(clean) >= 2:
                stemmed = self.preprocessor.stemmer.stem(clean)
                score = 1 if stemmed in query_set else 0
            else:
                score = 0
            word_scores.append(score)

        # Slide a small window across the text and keep the part with the most matches.
        best_start = 0
        best_score = 0
        window_size = max(1, max_length // 8)  # Approximate words per window

        for start in range(len(words)):
            end = min(start + window_size, len(words))
            score = sum(word_scores[start:end])
            if score > best_score:
                best_score = score
                best_start = start

        # Rebuild the chosen window using the original words.
        snippet_words = words[best_start:best_start + window_size]
        snippet = " ".join(snippet_words)

        if len(snippet) > max_length:
            snippet = snippet[:max_length].rsplit(" ", 1)[0]

        # Ellipses make it clear when text was cut from either side.
        if best_start > 0:
            snippet = "..." + snippet
        if best_start + window_size < len(words):
            snippet = snippet + "..."

        return snippet
