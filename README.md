# RESA Dashboard — VS Code local project

## Start on Windows
1. Extract this entire ZIP first.
2. Open VS Code > File > Open Folder > select RESA_Dashboard.
3. Open Terminal > New Terminal.
4. Run `py -3 run_local.py`.
5. Open http://localhost:8000 in your browser.
6. Press Ctrl+C in the terminal to stop.

Requires Python 3. No pip install, npm install, API key, or database is required.
If `py` is unavailable but Python is installed, run `python run_local.py`.
Alternatively double-click START_WINDOWS.bat after extracting the ZIP.
macOS/Linux: run `python3 run_local.py`.
If port 8000 is occupied: `py -3 run_local.py --port 8001`, then open http://localhost:8001.
Do not open index.html directly: the browser needs HTTP to load the dataset files.

## Files you can edit
- dist/index.html: HTML entry point.
- dist/app.js: React interface (plain JavaScript, no JSX build step).
- dist/styles.css: appearance and responsive layout.
- dist/engine.js: requirement checks and supplier scoring.
- dist/data/dashboard.json: data consumed by the interface.
- dist/data/raw/: downloaded public source files.
- dist/data/: demo records, evidence, dataset ZIP and source manifest.
- dist/vendor/: bundled React libraries.
- prepare_data.py: rebuild dashboard data from included sources; run from this folder.
- validate.cjs: optional scoring tests; run `node validate.cjs` if Node.js is installed.
- PROJECT_NOTES.md: dataset provenance, formula and research limitations.

## First-review demo
Open Decision workspace, assess the default brake-pad request, and inspect supplier evidence.
Change maximum delivery to seven days and reassess. Explore Supplier analytics and Datasets;
downloads work locally. Research evaluation contains four internal scenario checks.

## Implementation boundary
This is the working first-review frontend prototype with deterministic scoring and evidence checks.
It does not include a running FastAPI backend, LLM, Qdrant or hybrid-RAG pipeline.
Public datasets and clearly labelled synthetic scenario records are bundled separately.
Assessment date is fixed at 2026-09-11 for reproducibility.
React and datasets are bundled locally; optional Google Fonts may fall back to system fonts offline.
