# Final Frontend Checklist

## Build

```bash
npm install
npm run check
npm run build
```

Both commands should complete successfully before submission.

## Backend integration

Start FastAPI and verify:

- [ ] `/search` returns live ranked results
- [ ] result scores are supplied by backend
- [ ] `/search/explain` returns retrieval details
- [ ] phrase search works
- [ ] Boolean search works
- [ ] proximity search works if enabled
- [ ] `/publications` loads stored records
- [ ] `/publications/:id` loads publication details
- [ ] clustering status loads
- [ ] clustering prediction works
- [ ] clustering analytics load
- [ ] Task 1 evaluation loads
- [ ] system status loads
- [ ] crawl history loads when available

## Coursework correctness

- [ ] Frontend does not calculate TF-IDF
- [ ] Frontend does not calculate cosine similarity
- [ ] Frontend does not evaluate Boolean expressions
- [ ] Frontend does not implement phrase/proximity matching
- [ ] Frontend does not calculate clustering metrics
- [ ] Frontend does not train K-Means
- [ ] Human qrels are clearly identified
- [ ] Task 2 labels are described as evaluation/interpretation labels only
- [ ] No fake publication counts or metrics are displayed

## UX

- [ ] Light theme works
- [ ] Dark theme works
- [ ] Mobile navigation works
- [ ] `/` focuses search
- [ ] Skip-to-content works
- [ ] Keyboard focus is visible
- [ ] Offline banner works
- [ ] Search URLs remain shareable
- [ ] publication back-navigation works
- [ ] long pages show back-to-top control
- [ ] print preview is readable

## Screenshots worth taking for the report

- [ ] homepage
- [ ] search results for a good query
- [ ] Retrieval Details panel
- [ ] publication detail page
- [ ] advanced phrase or Boolean search
- [ ] clustering prediction
- [ ] clustering analytics
- [ ] Task 1 evaluation
- [ ] system/crawl dashboard
- [ ] About/architecture page

## Final rule

Do not change algorithms merely to make screenshots or metrics look better.
Evidence should represent the real backend and real evaluation.
