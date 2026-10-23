# Company Memory for Grounded Marketing Recommendations

A reproducible companion to the English industrial technical report **Company Memory for Grounded Marketing Recommendations: Separating Evidence Selection from Reader Performance** (23 October 2026).

The integrated study changes company context while holding the reader fixed: GPT-6.1 Sol and Claude Sonnet 5.5, seven contexts, 33 fictional worlds, 264 cases, 3,696 actual provider requests. A separate exploratory track compares raw documents with actual query-blind generic/marketing Markdown compilations on 22 external development questions from one fictional company. The release is an empirical research artifact, not a production product, a commercial ROI study, or an independent human assessment.

`paper/report.pdf` is the report; `paper/investor-note.pdf` is the two-page practical explanation. `MANIFEST.json` hashes every public file. `release/ACCEPTANCE.md` and `release/reproduction-records/clean-reproduction.json` identify the completed verification and its scope. A candidate archive is not yet a tested release. Packaging does not publish the private working repository or submit a paper. Historical PDFs and receipts remain in `release/history/`.

## What is compared

| Context | Implementation and boundary |
|---|---|
| None | Shared task/catalog without company evidence; information-availability reference |
| Generic hybrid | BM25 + real text-embedding-3-small vectors, reciprocal-rank fusion |
| Structured Markdown | Lossless entity files plus generic relation/authority diversity |
| GBrain search | Native pinned PGLite/balanced hybrid search; not the full product |
| Specialized coverage | Generic ranking plus public action-prerequisite coverage |
| GBrain + coverage | Identical selection layer over native GBrain candidates |
| Full current context | Every permitted seller/account record, with greater input consumption |

Every reader receives the same strong domain prompt and public action catalog. Primary allowance is 2,048 **UTF-8 evidence bytes**, not exact model tokens; actual tokens and cache usage are recorded. Original synthetic events and formal eligibility labels do not establish commercial strategic usefulness. The controlled Markdown arm is not an LLM compilation or an official Karpathy product. The external track is an actual, original wiki compiler inspired by that pattern; it is query-blind and receives no evaluation labels. Neither track proves universal specialized-memory superiority.

## Install and inexpensive offline checks

Use Python 3.12. Unit checks and scoring use only the standard library. Plotting requires the hash-pinned analysis environment. PDF compilation additionally requires system LaTeX/BibTeX, Pandoc and Poppler; observed versions are recorded in build receipts.

```sh
python3 -m venv .venv-analysis
.venv-analysis/bin/python -m pip install --require-hashes -r release/requirements-analysis.lock
.venv-analysis/bin/python -m unittest discover -s tests -v
.venv-analysis/bin/python -m unittest study.test_contract study.test_ledger analysis.test_analysis analysis.test_audit -v
.venv-analysis/bin/python -m study.fixtures --split test --worlds 33 --seed 2026102302 --output regenerated-data
.venv-analysis/bin/python -m study.reference --data data/integrated/main-v1 --output sql-reference-check
```

The regenerated input/label hashes must match `data/integrated/main-v1/manifest.json`; timestamps differ. These smoke/correctness checks make **zero API calls** and do not reproduce model inference.

## Recompute the integrated evidence without credentials

Use new output directories. This reconstructs every context packet from the saved real embedding vectors/native rankings, checks temporal/access boundaries, and re-scores raw model responses.

```sh
.venv-analysis/bin/python benchmarks/integrated/audit.py --data data/integrated/main-v1 --packets experiments/integrated/main-context-v1 --run experiments/integrated/main-reader-v1 --output reproduced-audit
.venv-analysis/bin/python benchmarks/integrated/analyze.py --run experiments/integrated/main-reader-v1 --data data/integrated/main-v1 --output reproduced-main
.venv-analysis/bin/python benchmarks/integrated/external_analyze.py --run experiments/integrated/external-reader-v1 --wiki experiments/integrated/external-wiki-compile-v4 --output reproduced-external
.venv-analysis/bin/python benchmarks/integrated/external_chunks.py --analyze experiments/integrated/external-chunks-v1 --output reproduced-chunks
.venv-analysis/bin/python benchmarks/integrated/figures.py --main reproduced-main/summary.json --context reproduced-audit/contexts.jsonl --external reproduced-external/summary.json --chunks reproduced-chunks/summary.json --output reproduced-figures
.venv-analysis/bin/python scripts/verify_report_claims.py
```

All attempted cases remain in denominators, including failures. Paired uncertainty resamples fictional worlds within family; it is not uncertainty over real customers. External 22-question QA is development evidence from one company, with no independent-company confidence interval. Citation-ID validity is not citation entailment. Costs are provider-usage/list-price estimates, not invoices; timed-out requests can have unknown billing.

## A fresh paid provider benchmark

Read `papers/marketing-memory/integrated-protocol-v0.1.md` and `benchmarks/integrated/providers.json` first. Models must still be available, and prices and quotas must be checked. Supply your own `RESEARCH_OPENAI_API_KEY` and `RESEARCH_ANTHROPIC_API_KEY` through the environment or a secret manager. No keys are included. The following plan command is offline; `--execute` sends real requests and can incur charges. The numerical cap is an operator guard, not a cost forecast.

```sh
python3 benchmarks/integrated/run.py --config benchmarks/integrated/providers.json --data data/integrated/main-v1 --packets experiments/integrated/main-context-v1 --output fresh-plan
python3 benchmarks/integrated/run.py --config benchmarks/integrated/providers.json --data data/integrated/main-v1 --packets experiments/integrated/main-context-v1 --output fresh-readers --execute --operational-cap-usd 300 --workers 16
```

This reruns readers over the exact saved contexts. To rerun native retrieval too, install the pinned GBrain/Bun dependencies in `benchmarks/gbrain/README.md`; the integrated path uses the included OpenAI embedding snapshot and **does not need a local Qwen tokenizer/model**:

```sh
python3 benchmarks/integrated/prepare.py --data data/integrated/main-v1 --output fresh-contexts --embedding-cache experiments/integrated/main-context-v1/embedding-cache-snapshot.jsonl --workers 2
```

For a fresh embedding acquisition, use a new empty cache path and add `--execute-embeddings --embedding-operational-cap-usd 1`. Native GBrain needs no provider credentials once vectors exist. Fresh provider generation can be stochastic or unavailable later; byte-identical analysis reproduction is a separate claim from fresh inference.

An additional 44-call chunked-BM25 development control is explicitly post-hoc; it corrects the whole-document packer’s inability to include an oversized contract. Its original comparator scores remain unchanged. `external_sensitivity.py` separately recomputes the disclosed one-label sensitivity.

Actual wiki compilation and external QA are separately paid operations:

```sh
python3 benchmarks/integrated/external_wiki.py --compile --output fresh-wikis --operational-cap-usd 5
python3 benchmarks/integrated/external_evaluate.py --wiki fresh-wikis --output external-plan --operational-cap-usd 150
python3 benchmarks/integrated/external_evaluate.py --wiki fresh-wikis --output fresh-external --operational-cap-usd 150 --execute --workers 12
python3 benchmarks/integrated/external_chunks.py --output fresh-external-chunks --execute --operational-cap-usd 10
```

The compiler uses native OpenAI background responses and polls the same response ID. The synchronous transport failures remain in the release. No automatic favorable-answer retries or test-question-driven wiki refinement is performed.

## Compile and verify an extracted archive

```sh
.venv-analysis/bin/python scripts/compile_investor_note.py --output rebuilt/investor-note.pdf
.venv-analysis/bin/python scripts/compile_paper.py --output rebuilt/report.pdf
.venv-analysis/bin/python scripts/reproduce_saved.py --output clean-reproduction
```

The last command requires an extracted archive with its `MANIFEST.json`. It verifies all public hashes, runs tests, rebuilds both historical and integrated analyses/figures, and recompiles both PDFs. It uses saved outputs and no provider credentials. The recorded clean check used a separate extracted directory and isolated Python environment on the same hardware, with system TeX; it is not an independent external replication.

## Evidence map and licenses

- `experiments/integrated/main-freeze-v1.json`: prospective code/data freeze; `main-reader-v1/`: every request, raw response, usage and score.
- `analysis/integrated/`: pilot/main summaries, per-attempt outcomes, context/response audit and external QA.
- `literature/`: search methodology, comparison matrix and critical reviews; metadata-only public indexes exclude copied abstracts/PDFs.
- `data/integrated/`: original fictional worlds; `data/external/messy-company-v1/`: MIT upstream development material and fetch hashes.
- `release/CLAIMS.json`: quantified claims mapped to hashed evidence; `THIRD_PARTY.md`: provenance and exclusions.

Original research code: MIT. Original data/documentation: CC BY 4.0, subject to the scope in `LICENSE-DATA`. Upstream company documents retain their MIT license/credits. GBrain is separately installed under MIT. Proprietary models and their services are not licensed by this package. Model-generated outputs are identified as such, not human-authored ground truth. No production code, customer records, private planning history, credentials, model weights or third-party paper PDFs are included.
