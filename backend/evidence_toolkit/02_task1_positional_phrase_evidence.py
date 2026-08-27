from __future__ import annotations

import argparse

from common import banner, emit_and_save
from indexing.index_manager import IndexManager
from preprocessing.text_preprocessor import TextPreprocessor


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print Task 1 positional-index and exact phrase-search evidence."
    )
    parser.add_argument(
        "--terms",
        nargs="+",
        default=["student", "postgradu"],
        help="Processed terms whose stored positions should be displayed.",
    )
    parser.add_argument(
        "--phrase",
        default="postgraduate students",
        help="Phrase to preprocess and run through phrase_search().",
    )
    args = parser.parse_args()

    manager = IndexManager()
    manager.load()
    processor = TextPreprocessor()

    lines = [
        banner("TASK 1 — POSITIONAL INDEX + PHRASE SEARCH EVIDENCE"),
        "Stored positional postings",
        "Format: {document_id: [token_position, ...]}",
    ]

    for term in args.terms:
        positions = dict(manager.positional_index.positions.get(term, {}))
        lines.extend(["", f"Term: {term}", f"Positions: {positions}"])

    phrase_tokens = processor.phrase_tokens(args.phrase)
    phrase_results = manager.positional_index.phrase_search(phrase_tokens)
    lines.extend(
        [
            "",
            "Exact phrase-search demonstration",
            f"Original phrase: {args.phrase!r}",
            f"Processed phrase tokens: {phrase_tokens}",
            f"Matching document IDs: {phrase_results}",
        ]
    )

    emit_and_save("02_task1_positional_phrase_evidence", lines)


if __name__ == "__main__":
    main()
