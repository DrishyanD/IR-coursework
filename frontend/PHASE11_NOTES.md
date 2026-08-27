# Phase 11 verification checklist

Run:

```bash
npm install
npm run check
npm run build
npm run dev
```

Manual checks:

1. Press `/` from a normal page and confirm the nearest visible search input gets focus.
2. Confirm `/` does not steal focus while typing in another input or textarea.
3. Turn browser network offline and confirm the offline banner appears.
4. Navigate using keyboard only and verify visible focus indicators.
5. Use the skip-to-content link with Tab from the top of the page.
6. Resize to mobile width and verify navigation remains usable.
7. Open a long page and verify the back-to-top button appears.
8. Test light and dark appearance.
9. Test browser print preview on Evaluation/System pages.
10. Trigger a known API error and confirm the existing page-level error UI remains readable.
11. Verify page titles change with routes.
12. Confirm no frontend action performs IR calculations that belong to Python.
