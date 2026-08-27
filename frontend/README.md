# Frontend

This is the React + TypeScript interface for the coursework project. It contains the publication search pages, publication details, clustering page and Data Management page for manual/scheduled crawler updates.

## Start

```bash
npm install
npm run dev
```

The frontend normally runs at `http://localhost:5173`.

Copy `.env.example` to `.env` if you need to change the backend address:

```text
VITE_API_BASE_URL=http://localhost:8000
```

## Check before pushing

```bash
npm run check
npm run build
```

The frontend only displays results and sends requests. The actual crawling, indexing, ranking and clustering logic stays in the Python backend.
