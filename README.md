# Information Retrieval Coursework

This is my ST7071CEM Information Retrieval coursework project. It contains the two tasks from the assignment in one web application.

- **Task 1:** a vertical search engine for publications from Coventry University's Centre for Healthcare and Community Transformation.
- **Task 2:** a K-Means document clustering system using BBC RSS/news text from Economics, Entertainment and Politics.

The backend is written in Python with FastAPI and the frontend is React + TypeScript.

## Main features

### Task 1

- Crawls the configured Coventry PurePortal area.
- Checks `robots.txt`, limits the crawl scope and waits between requests.
- Uses RSS links to help discover publication pages.
- Extracts publication details such as title, authors, date, DOI, abstract and profile links.
- Stores the data in SQLite.
- Builds a custom vocabulary, inverted index and positional index.
- Ranks keyword searches with TF-IDF and cosine similarity.
- Supports phrase, Boolean and NEAR-k searches.
- Can run updates manually or automatically once a week.
- Includes retrieval evaluation using a small manually judged qrels set.

### Task 2

- Uses a BBC-derived corpus with Economics, Entertainment and Politics documents.
- Converts the text to TF-IDF features.
- Trains a 3-cluster K-Means model.
- Saves the trained model and vectorizer.
- Shows clustering evaluation such as Silhouette, ARI, NMI and V-measure.
- Lets the user paste new text (or load a supported article) and assigns it to the nearest learned cluster.

## Project folders

```text
backend/    Python crawler, indexing, search, clustering, API and tests
frontend/   React/TypeScript user interface
```

The backend already contains the coursework dataset, saved indexes and the trained clustering model, so the project can be demonstrated without rebuilding everything first.

## Run the backend

Python 3.11+ is recommended.

```bash
cd backend
python -m venv .venv
```

Activate the environment:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install the packages:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. An OpenAlex API key is optional for the saved demo data, but it can be added if you want to run fresh enrichment requests.

Start FastAPI:

```bash
uvicorn main:app --reload
```

The API will run on `http://localhost:8000` and FastAPI documentation is available at `http://localhost:8000/docs`.

## Run the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will normally open at `http://localhost:5173`.

If the backend is running somewhere else, copy `frontend/.env.example` to `frontend/.env` and change `VITE_API_BASE_URL`.

## Useful commands

Run the backend tests. The live PurePortal extraction test is skipped automatically if the site is unavailable:

```bash
cd backend
pytest -q
```

Check and build the frontend:

```bash
cd frontend
npm run check
npm run build
```

Run the evidence scripts from the backend folder:

```bash
python evidence_toolkit/01_task1_index_evidence.py
python evidence_toolkit/02_task1_positional_phrase_evidence.py
python evidence_toolkit/03_task1_evaluation_evidence.py
python evidence_toolkit/04_task2_evidence.py
python evidence_toolkit/08_scheduler_evidence.py
```

## Notes

The repository includes the data and saved model used for the coursework demonstration. Fresh web crawling depends on the external Coventry/OpenAlex/BBC services being reachable at the time it is run.

