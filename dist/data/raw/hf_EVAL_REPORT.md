# Auto-Parts-Search v3 — Public Eval Report

> **Model:** [`ManmohanBuildsProducts/auto-parts-search-v3`](https://huggingface.co/ManmohanBuildsProducts/auto-parts-search-v3)
> **Benchmark:** [`ManmohanBuildsProducts/auto-parts-search-benchmark`](https://huggingface.co/datasets/ManmohanBuildsProducts/auto-parts-search-benchmark) (dev set, 149 queries)
> **Reproducibility:** `scripts/bench_external.py` + `scripts/bench_production.py`
> **Judge:** DeepSeek V3 chat (joint-pool LLM grading)
> **Dates:** 2026-04-15

## 1. What this measures

Indian auto-parts retrieval quality across Hindi/Hinglish, misspellings, brand-as-generic usage, symptom queries, and part numbers. Built to answer: *does a small domain-tuned embedding model (ours) compete with general-purpose commercial embeddings (OpenAI, Cohere, Jina) on a retrieval task where Indic language shape + catalog noise matters?*

## 2. What gets compared

Two corpora, because honest retrieval numbers depend on corpus:

- **Round 1 — KG corpus (2,121 docs):** curated part-name + alias + system entries. "Clean" semantic retrieval.
- **Round 2 — Production corpus (26,835 docs):** the actual index behind our `/search` endpoint. 884 KG + 25,951 catalog products. Catalog text is noisy: brand names, vehicle fitments, part numbers interleaved with generic descriptions.

Six embedding models (round 2 drops Jina v3 — API rate limits made 26K embed impractical at free tier):

| Model | Dim | Where | Cost per 1M tokens (input) |
|---|---:|---|---:|
| `openai/text-embedding-3-large` | 3072 | API | $0.13 |
| `cohere/embed-multilingual-v3.0` | 1024 | API | $0.10 |
| `jinaai/jina-embeddings-v3` | 1024 | API | $0.02 |
| `intfloat/multilingual-e5-large` | 1024 | Local | $0 |
| `BAAI/bge-m3` | 1024 | Local | $0 |
| **`ManmohanBuildsProducts/auto-parts-search-v3`** (ours) | **1024** | **Local** | **$0** |

Plus our production hybrid: `v3+bm25-hybrid` (Meilisearch BM25 + v3 dense + class-weighted RRF).

## 3. Methodology (why these numbers should be trusted)

1. **Joint-pool LLM judging.** For each query, the top-20 docs from *every model* are unioned into a single candidate pool (median ~60 docs). DeepSeek V3 grades each (query, doc) pair on a 0/1/2 scale. Then every model is scored against this same judged pool — no model is judged on an advantage-home set.
2. **Same 149 dev queries, 6 query types** — `exact_english`, `misspelled`, `hindi_hinglish`, `symptom`, `brand_as_generic`, `part_number`. Balanced 22–27 per type. Generated from scraped catalog + mechanic interviews, stratified sample from a 195-query master (46 held as sealed test, see limitations).
3. **Judge choice: DeepSeek V3 chat.** Neutral (no family relationship to benched embedding models), robust on long pools. Prior calibration measured 96% query-level agreement with Claude Opus on this task. We use V3 (non-reasoning) because V3's reasoning model exhausts the token budget on pools >50.
4. **Per-model query/doc conventions respected.** OpenAI: no prefix. Cohere: `input_type="search_query"|"search_document"`. Jina: `task="retrieval.query"|"retrieval.passage"`. e5: `"query: "|"passage: "` prefixes. BGE-m3 and v3: no prefix. Pre-validated by canonical-query sanity check.
5. **Metrics:** graded nDCG@10, Recall@5 (grade=2), P@1, MAP@10, zero-result rate @10, plus per-category nDCG@10.

All code and cached embeddings available at the repo. Rerunnable with three API keys (OpenAI ≈ $0.11, Cohere/Jina free tier) + DeepSeek ≈ $0.30.

## 4. Results — Round 1 (KG corpus, 2,121 docs)

| Model | nDCG@10 | Recall@5 | P@1 | MAP@10 | 0-result@10 |
|---|---:|---:|---:|---:|---:|
| `openai-3-large` | **0.539** | **0.483** | 0.611 | 0.466 | 16.1% |
| **`v3-ours`** | 0.477 | 0.378 | **0.631** | **0.505** | 21.5% |
| `cohere-mult-v3` | 0.395 | 0.317 | 0.591 | 0.461 | 20.1% |
| `jina-v3` | 0.388 | 0.300 | 0.523 | 0.464 | 26.8% |
| `bge-m3` | 0.369 | 0.347 | 0.490 | 0.391 | 24.2% |
| `e5-large` | 0.356 | 0.318 | 0.523 | 0.420 | 21.5% |

**Per-category nDCG@10:**

| Model | brand_as_generic | exact_english | hindi_hinglish | misspelled | part_number | symptom |
|---|---:|---:|---:|---:|---:|---:|
| `openai-3-large` | **0.601** | **0.732** | 0.526 | 0.595 | **0.252** | **0.503** |
| `v3-ours` | 0.436 | 0.675 | **0.548** | **0.637** | 0.106 | 0.424 |
| `cohere-mult-v3` | 0.363 | 0.609 | 0.393 | 0.500 | 0.096 | 0.376 |
| `jina-v3` | 0.374 | 0.545 | 0.483 | 0.521 | 0.073 | 0.301 |
| `bge-m3` | 0.324 | 0.582 | 0.360 | 0.531 | 0.082 | 0.309 |
| `e5-large` | 0.343 | 0.497 | 0.351 | 0.527 | 0.099 | 0.304 |

### Round 1 takeaways
- v3 is **#2 of 6**. Beats every open-source model and every non-OpenAI commercial model.
- v3 is **#1 on P@1** (0.631) and **#1 on MAP@10** (0.505) — sharpest at the top-1.
- v3 beats OpenAI on **Hindi/Hinglish** (+2.2pts) and **misspelled** (+4.2pts) — directional; deltas within the ±10% per-category MoE at n=22–27.

## 5. Results — Round 2 (Production corpus, 26,835 docs)

| Model | nDCG@10 | Recall@5 | P@1 | MAP@10 | 0-result@10 |
|---|---:|---:|---:|---:|---:|
| `openai-3-large` | **0.468** | **0.290** | **0.550** | **0.477** | 32.9% |
| **`v3+bm25-hybrid-tuned`** (our production, 3-fold CV) | **0.424** | 0.257 | 0.523 | 0.458 | 33.6% |
| `v3-ours` (embedding only) | 0.411 | 0.240 | 0.503 | 0.439 | 34.9% |
| `v3+bm25-hybrid` (pre-tune) | 0.400 | 0.242 | 0.483 | 0.426 | 33.6% |
| `cohere-mult-v3` | 0.332 | 0.218 | 0.456 | 0.379 | 36.2% |
| `e5-large` | 0.309 | 0.221 | 0.450 | 0.360 | 36.9% |
| `bge-m3` | 0.307 | 0.194 | 0.403 | 0.328 | 35.6% |

**Per-category nDCG@10:**

| Model | brand_as_generic | exact_english | hindi_hinglish | misspelled | part_number | symptom |
|---|---:|---:|---:|---:|---:|---:|
| `openai-3-large` | **0.499** | 0.480 | **0.544** | 0.526 | **0.178** | **0.555** |
| `v3+bm25-hybrid-tuned` | 0.415 | **0.531** | 0.460 | **0.544** | 0.099 | 0.497 |
| `v3-ours` | 0.353 | 0.514 | 0.440 | 0.538 | 0.084 | 0.495 |
| `cohere-mult-v3` | 0.369 | 0.413 | 0.380 | 0.432 | 0.068 | 0.313 |
| `e5-large` | 0.410 | 0.296 | 0.382 | 0.474 | 0.047 | 0.252 |
| `bge-m3` | 0.311 | 0.287 | 0.360 | 0.439 | 0.056 | 0.373 |

### Round 2 takeaways
- Production tuned hybrid is **#2 of 7 systems** on a 26K-doc catalog-heavy corpus.
- Production tuned hybrid **beats OpenAI on 2 of 6 query categories**: `exact_english` (+5.1pts) and `misspelled` (+1.8pts).
- Production tuned hybrid loses to OpenAI on `hindi_hinglish` (−8.4pts), `brand_as_generic` (−8.4pts), `part_number` (−7.9pts). Note: in round 1 (clean KG corpus), v3 beat OpenAI on Hindi — the regression appears on catalog-style data that v3 was never trained on.
- Fusion-weight tuning (grid search + coordinate descent over the 5 classifier classes) lifted hybrid overall nDCG@10 from 0.400 → 0.424 (+6.0%) as measured by 3-fold CV (stratified by query_type, seed 42). In-sample tuned nDCG = 0.4313; overfit gap = +0.0075 (0.75pts). Largest per-category lifts held in CV: `brand_as_generic` and `exact_english`.

## 6. What this says about v3

**Core strengths (both corpora):**
- **Clean English retrieval** — beats OpenAI on production corpus exact_english by 5.1pts.
- **Misspelling tolerance** — beats OpenAI in both rounds.
- **Top-1 precision** — highest P@1 in round 1, very close to OpenAI in round 2.
- **Runs at $0.** 1024-dim, 568M params, fine-tuned from BGE-m3, deploys on any CPU.

**Known limits (both corpora):**
- **Part numbers are a structural miss** for pure embedding retrieval. v3 returns "Latches/Locks" for `6U7853952`. BM25 closes some of this gap but not all.
- **Hindi on catalog data degrades** (v3 wins Hindi in round 1 / loses in round 2). v3 was fine-tuned on clean KG-style Hindi pairs; catalog-style mixed English + brand + Hindi confuses it.
- **Brand-as-generic on catalog** is the biggest single category loss. Similar explanation.

## 7. Limitations (read before citing these numbers)

1. **n = 149 dev queries.** Overall nDCG@10 MoE ≈ ±3-5% at 95% CI. Per-category at n=22-27: MoE ≈ ±10%. Small per-category deltas are noise; we've flagged which results are within MoE.
2. **Fusion-weight tuning was validated via 3-fold CV** (stratified by query_type, seed 42). In-sample tuned nDCG@10 = 0.4313; held-out-across-3-folds average = 0.4238. Overfit gap = +0.0075 (small). All numbers reported above use the CV held-out estimate. The sealed 46-query test set remains reserved for a follow-up publication.
3. **LLM judge, not human.** DeepSeek V3 at temperature 0. Prior calibration: 96% query-level agreement with Claude Opus on this task (measured 2026-04-13). Judge output is not fully deterministic on rerun.
4. **Corpus is Indian auto-parts-specific.** Results do not generalize to general-purpose retrieval or to other e-commerce domains.
5. **The hybrid's BM25 component uses our `IndicTokenizer`** — dual-script expansion (Roman↔Devanagari) tuned for Hindi queries. A third party running vanilla BM25 would get different numbers.
6. **v3 was fine-tuned on 26,760 pairs** (see `data/training/golden/METADATA.md`). Full provenance + SHA256 hashes published at the benchmark repo.

## 8. How to reproduce

```bash
git clone https://github.com/ManmohanBuildsProducts/auto-parts-search  # TODO public
cd auto-parts-search
pip install -r requirements.txt
python3 -m playwright install chromium
python3 -m auto_parts_search build-graph-db   # builds data/knowledge_graph/graph.db

# Set up keys
export OPENAI_API_KEY=sk-...
export COHERE_API_KEY=...
export JINA_API_KEY=...      # for round 1 only
export DEEPSEEK_API_KEY=sk-...

# Round 1 — KG-only (cheap, ~$0.06 + ~25min LLM judge)
python3 -m scripts.bench_external all

# Round 2 — production 26K (slower, ~$0.20 + ~25min LLM judge)
python3 -m scripts.bench_production corpus
python3 -m scripts.bench_production embed
python3 -m scripts.bench_production pool
python3 -m scripts.bench_production judge
python3 -m scripts.tune_hybrid    # grid-search fusion weights
python3 -m scripts.bench_production hybrid
python3 -m scripts.bench_production score
python3 -m scripts.bench_production report
```

Cached embeddings + graded-pool JSONL are mirrored in the HF dataset repo.

## 9. Citation

```bibtex
@misc{auto_parts_search_bench_2026,
  author       = {Khurana, Manmohan},
  title        = {Auto-Parts-Search: Indian Automotive Retrieval Benchmark + v3 Model Card},
  year         = 2026,
  publisher    = {Hugging Face},
  url          = {https://huggingface.co/datasets/ManmohanBuildsProducts/auto-parts-search-benchmark},
}
```

## 10. Contact

Manmohan Khurana — solo founder, building an Indic-first auto-parts search layer.
`manmohanbuildsproducts [at] gmail.com`
