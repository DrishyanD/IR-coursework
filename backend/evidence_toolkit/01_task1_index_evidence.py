from __future__ import annotations

import argparse

from common import banner, emit_and_save
from indexing.index_manager import IndexManager


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print screenshot-friendly Task 1 inverted-index evidence."
    )
    parser.add_argument(
        "--terms",
        nargs="+",
        default=["yoga", "student", "postgradu"],
        help="Processed index terms to inspect.",
    )
    args = parser.parse_args()

    manager = IndexManager()
    manager.load()
    stats = manager.stats()

    lines = [
        banner("TASK 1 — INVERTED INDEX EVIDENCE"),
        f"Indexed documents:        {stats['documents']}",
        f"Vocabulary size:          {stats['vocabulary_size']}",
        f"Terms with postings:      {stats['terms_with_postings']}",
        f"Positional index terms:   {stats['positional_index_terms']}",
        f"Sorted postings enabled:  {stats['sorted_postings']}",
        "",
        "Readable posting-list examples",
        "Format: [(document_id, term_frequency), ...]",
    ]

    for term in args.terms:
        postings = manager.inverted_index.sorted_postings(term)
        df = manager.inverted_index.document_frequency(term)
        lines.extend(
            [
                "",
                f"Term: {term}",
                f"Document frequency: {df}",
                f"Postings: {postings}",
            ]
        )

    emit_and_save("01_task1_index_evidence", lines)


if __name__ == "__main__":
    main()
