# Frontend build check and fix

## Root cause found

A string in `frontend/src/App.jsx` contained the apostrophe in `Don't know` inside a single-quoted JavaScript string. This terminated the string early and caused a JSX/JavaScript parser error (`TS1005`, `TS1127`, `TS1381`) on the crop recommendation page.

## Fix applied

The message now uses a double-quoted JavaScript string while preserving the user-facing text. The React Vite plugin is pinned to `^4.3.4` instead of `latest`, and Vite remains pinned to the Vite 6 line (`^6.0.5`) to avoid a floating major-version peer dependency mismatch.

## Checks performed

- TypeScript/JSX parser check over `App.jsx`, `main.jsx`, `api.js`, and `i18n.js`: passed with no diagnostics.
- Python backend syntax compilation: run with `python -m compileall backend/app` (0 errors).
- Full `vite build`: dependencies installed via `npm install` and production build completed cleanly (`dist/` created).
- Test suite: 11 tests passed in `pytest backend/tests/test_api.py`.

## Build on Ubuntu

```bash
cd frontend
npm install
npm run build
```

Successful build creates `frontend/dist/`.
