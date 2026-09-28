---
language:
  - en
  - hi
license: cc-by-4.0
task_categories:
  - text-retrieval
pretty_name: Auto-Parts-Search Benchmark (Indian Automotive Retrieval)
size_categories:
  - n<1K
tags:
  - retrieval
  - indic
  - hindi
  - hinglish
  - e-commerce
  - automotive
  - benchmark
---

# Auto-Parts-Search Benchmark

> A public, reproducible retrieval benchmark for **Indian automotive parts search** — Hindi / Hinglish / English / misspellings / brand-as-generic / symptom / part-number query types. Built to let anyone independently verify claims about domain-tuned vs commercial embedding models on this task.

Companion to the model [`ManmohanBuildsProducts/auto-parts-search-v3`](https://huggingface.co/ManmohanBuildsProducts/auto-parts-search-v3) and the full eval writeup in [`docs/EVAL_REPORT.md`](https://github.com/ManmohanBuildsProducts/auto-parts-search/blob/master/docs/EVAL_REPORT.md).

## What's inside

| Split | File | Queries | Use |
|---|---|---:|---|
| **dev** | `benchmark_dev.json` | 149 | Tuning + reporting |
| **test (SEALED)** | `benchmark_test.json` | 46 | **Do not tune on this.** Reserved for follow-up publication. |

Each query:
```json
{
  "query": "engine garam ho raha",
  "query_type": "symptom",
  "expected_parts": ["radiator", "thermostat", "coolant"],
  "expected_categories": [],
  "expected_vehicles": [],
  "difficulty": "easy",
  "notes": ""
}
```

**Query types (149 dev queries):**

| Type | n | Example |
|---|---:|---|
| `exact_english` | 27 | "brake pad for Swift" |
| `misspelled` | 23 | "break pad" |
| `hindi_hinglish` | 27 | "गाड़ी का brake" or "gaadi ki batti" |
| `symptom` | 27 | "engine garam ho raha" |
| `brand_as_generic` | 22 | "Mobil for Swift", "Amaron for Innova" |
| `part_number` | 23 | "6U7853952" |

## Graded relevance labels

`round1_graded.jsonl` and `round2_graded.jsonl` contain **LLM-judged relevance grades** for each (query, candidate) pair:
- `2` = RELEVANT (direct match)
- `1` = MARGINAL (related but not direct)
- `0` = IRRELEVANT

**Judge:** DeepSeek V3 (chat), temperature 0. Prior calibration showed 96% query-level agreement with Claude Opus on this task.

**Pool construction:** for each query, the top-20 hits from *every* evaluated model are unioned into a joint pool (median ~60 docs), then judged once. This eliminates per-model bias — every model is scored against the same judged pool.

## Corpora

- **Round 1 — KG corpus (2,121 docs):** curated auto-parts knowledge graph entries (names + aliases + parent systems).
- **Round 2 — Production corpus (26,835 docs):** the full index behind our production `/search` endpoint. 884 KG + 25,951 scraped catalog products (SparesHub, Eauto, Bikespares).

`round2_corpus.json` contains the (id, text, metadata) triples for the 26,835 production corpus.

## Results summary (round 2, production corpus)

| Model | nDCG@10 | R@5 | P@1 | MAP@10 |
|---|---:|---:|---:|---:|
| openai/text-embedding-3-large | **0.468** | 0.290 | 0.550 | 0.477 |
| **v3+BM25 hybrid (tuned, 3-fold CV)** | **0.424** | 0.257 | 0.523 | 0.458 |
| v3 (embedding only) | 0.411 | 0.240 | 0.503 | 0.439 |
| cohere/embed-multilingual-v3.0 | 0.332 | 0.218 | 0.456 | 0.379 |
| intfloat/multilingual-e5-large | 0.309 | 0.221 | 0.450 | 0.360 |
| BAAI/bge-m3 | 0.307 | 0.194 | 0.403 | 0.328 |

Full results + per-category breakdowns: see `round2_scores.json` and `EVAL_REPORT.md`.

## How to use

```python
from datasets import load_dataset
ds = load_dataset("ManmohanBuildsProducts/auto-parts-search-benchmark", data_files="benchmark_dev.json")
print(ds["train"][0])
```

Or just:
```python
import json
queries = json.load(open("benchmark_dev.json"))
```

## Reproducibility

Full pipeline at [github.com/ManmohanBuildsProducts/auto-parts-search](https://github.com/ManmohanBuildsProducts/auto-parts-search). Bench scripts:
- `scripts/bench_external.py` — round 1 (KG only)
- `scripts/bench_production.py` — round 2 (production corpus)
- `scripts/tune_hybrid.py` + `scripts/tune_hybrid_cv.py` — fusion-weight tuning

Cost to reproduce full round 2: ~$0.20 OpenAI embeddings + ~$0.30 DeepSeek judge. Cohere/Jina fit within free tiers.

## Limitations

1. **n = 149 dev queries.** Overall nDCG@10 MoE ≈ ±3–5% at 95% CI; per-category (n=22–27) MoE ≈ ±10%. Small per-category deltas are noise.
2. **LLM judge, not human.** DeepSeek V3 at temperature 0, calibrated against Claude Opus at 96% agreement.
3. **Indic auto-parts-specific.** Does not generalize to other e-commerce domains.
4. The **hybrid's BM25 uses a custom Indic tokenizer** (Roman↔Devanagari expansion) — third parties running vanilla BM25 will get different hybrid numbers.

## Citation

```bibtex
@misc{auto_parts_search_bench_2026,
  author    = {Khurana, Manmohan},
  title     = {Auto-Parts-Search: Indian Automotive Retrieval Benchmark + v3 Model Card},
  year      = 2026,
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/ManmohanBuildsProducts/auto-parts-search-benchmark},
}
```

## License

- **This benchmark dataset:** CC-BY-4.0 (attribution required; any use incl. commercial).
- **Companion v3 model:** Apache-2.0 (inherits from BGE-m3 MIT, upgraded to Apache-2.0 for patent grant).

## Contact

Manmohan Khurana — `manmohanbuildsproducts [at] gmail.com`
