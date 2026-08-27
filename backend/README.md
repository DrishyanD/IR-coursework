# Backend

This folder contains the Python side of the coursework: crawling, extraction, SQLite storage, indexing, ranked search, evaluation, clustering and FastAPI routes.

## Start

```bash
python -m venv .venv
# activate the environment
pip install -r requirements.txt
uvicorn main:app --reload
```

The main API is available at `http://localhost:8000` and the interactive docs are at `/docs`.

## Useful folders

- `crawler/` - PurePortal crawler, scheduler and update pipeline
- `extraction/` - publication parsing and validation
- `indexing/` - custom vocabulary, inverted/positional indexes and TF-IDF
- `search/` - query processing, ranking and snippets
- `clustering/` - Task 2 TF-IDF/K-Means training and prediction
- `evaluation/` - retrieval/clustering metrics
- `evidence_toolkit/` - small scripts used to reproduce report evidence
- `tests/` - pytest tests

The saved SQLite database, indexes and clustering model are included for the coursework demo.
