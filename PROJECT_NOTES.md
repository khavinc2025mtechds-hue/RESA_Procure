# RESA · First-review dashboard

Evidence-Grounded Supplier Intelligence for Automotive Procurement. Khavin C, T9972, Rajalakshmi Engineering College.

## Scope
React 18 frontend with locally bundled React libraries and static JSON/CSV snapshots. The review scenario implements deterministic requirement checks and a documented suitability score. It does not run Qdrant, Ollama, FastAPI, embeddings or an LLM. These remain the agreed research implementation target.

Views: supplier decision workspace, public supplier analytics, synthetic evidence library, dataset explorer, research evaluation plan. The dashboard lets users change mandatory constraints, inspect exact supporting records and export an assessment. Original public files and a source manifest are available for download.

## Data
- Procurement KPI Analysis by Shahriar Kabir: 777 downloaded rows, publisher-described real/anonymized generic procurement. The publisher description says 700; the actual CSV contains 777. CC0 per publisher metadata. No automotive identity mapping. No currency or promised-delivery-date field.
- Graph Dataset Hub supply chain: 50 public sample rows across suppliers, parts, vehicle models and supply relationships. Raw duplicate links retained. No cross-source supplier joins.
- Auto-Parts Search Benchmark by ManmohanBuildsProducts: 149 development queries, CC BY 4.0. Sealed test split deliberately excluded.
- Generated review scenario: 6 fictional suppliers, 12 quotations, 18 scorecards and 1 policy, plus 4 test scenarios. Synthetic data are clearly labelled and separate from public records.

Source URLs, downloaded-file SHA256 hashes and limitations: `dist/data/manifest.json`. Downloadable data package: `dist/data/RESA_First_Review_Datasets.zip`.

## Run
Serve `dist` using any static HTTP server, for example `python -m http.server 8000 --directory dist`, then open http://localhost:8000. Open through HTTP so the data fetch works.

## Validate
`node --check dist/app.js` and `node validate.cjs`. Scenario checks are implementation tests, not model performance results.

The dashboard uses a fixed assessment date, 2026-09-11, for reproducible review scenarios. A future implementation should use the procurement query's assessment date.

## Method
Hard requirements screen candidates before scoring. Missing or stale evidence triggers review. Demo score = 0.25 quality + 0.20 price + 0.20 delivery + 0.20 reliability + 0.15 evidence coverage - 0.15 risk, bounded to [0,100]. Scorecard freshness window: 120 days. Price min-max scaling is component-specific. Defect constraint is strict '<'. Weight choices are illustrative and not learned. Evidence coverage includes known satisfied and violated states. No research-result claims are made.

The app checks exact JSON records, not the semantic entailment of arbitrary documents. Risk histories remain synthetic. Baseline/ablation experiments and independently annotated supplier-ranking labels are future work.
