# Evidence Selection in B2B Marketing Memory

Reproducible companion to **Evidence Selection in B2B Marketing Memory: A Preliminary Component Study**, an AI-assisted industrial technical report (2026).

Six adapters select evidence from common verified fictional events for one shared local reader. The task is a supported catalog decision, not natural-language ingestion, strategic usefulness, campaign ROI, production validation or a comparison of complete commercial memory products. An exact SQL reference solves the formal eligibility contract directly.

This revision separates **context provision** from **action recommendation**, adds an actual pinned GBrain hybrid-search component comparison and a same-backend prerequisite-selection control, and tests wider context allowances. The original frozen reader experiment is unchanged. The GBrain extension reuses already observed fictional cases and is exploratory. It does not rank hosted GBrain, its paid/graph/ingestion configuration, or whole-company systems.

Two prospective studies are specified in `papers/marketing-memory/protocol-v0.1.md` and `papers/marketing-recommendation/protocol-v0.1.md`. The latter has a tested fixed-context Claude/GPT pilot runner with explicit model, credential, price and spending requirements; **no Claude/GPT results exist yet**. A hash-verified external development corpus is included with its upstream MIT attribution; downloading it is not a completed ingestion study. Current report readiness and completion of that broader research program are distinct.

In the empirical archive, `paper/report.pdf` is the report and `paper/investor-note.md` explains the practical implications. `MANIFEST.json` hashes every included file. `release/ACCEPTANCE.md` and `release/reproduction-records/clean-reproduction.json` identify verified checks and limits. An archive marked `empirical_release_candidate` has not passed the clean-reproduction gate. Packaging does not publish the private working repository or submit the paper.

Exact v1 PDFs and acceptance receipts remain under `release/history/v1/`.

## New comparisons and their evidence boundary

- `experiments/gbrain/`: all real upstream attempts, including integration/cache failures, original requests/rankings and source snapshots. Corrected exploratory run: `exploratory-96-v2`.
- `analysis/gbrain/reproducible-{1024,1536,4096}/`: context-only scores, selected source IDs, paired descriptive summaries and actual tokenizer receipts. No recommendation or revenue number is inferred from them.
- `analysis/context-v1/`: explicitly post-hoc separation of evidence availability from the existing reader's decisions.
- `benchmarks/recommendation/`: offline plan and capped real-provider runner. Dry-run plans and tests are not provider results.

Saved GBrain analysis can be regenerated **without Bun, model weights or a running model service**:

```sh
python benchmarks/gbrain/analyze.py --run experiments/gbrain/exploratory-96-v2 \
  --data data/study/main-v1 --cache experiments/main/primary/embeddings.jsonl \
  --offline-token-counts analysis/gbrain/reproducible-1024/token-counts.json \
  --output reproduced-gbrain-1024
```

For 1,536 and 4,096, add the matching `--token-cap` and receipt path. This replays
actual saved native rankings, real embeddings and tokenizer counts; it does not
rerun GBrain. `benchmarks/gbrain/README.md` documents the actual native path and
its excluded features. Fresh execution requires pinned upstream code, Bun and
the documented local tokenizer/embedding resources. The full saved reproduction
command below covers all three packet budgets and both context diagnostics.

## Offline checks: no model calls

Use Python 3.12 from the extracted archive root. These commands need no packages or credentials:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest study.test_contract study.test_ledger analysis.test_analysis analysis.test_audit -v
python3 scripts/verify_report_claims.py
python3 -m study.fixtures --split test --worlds 12 --seed 2026102202 --output reproduced-data
python3 -m study.reference --data data/study/main-v1 --output reproduced-sql-reference
```

The regenerated input/label hashes must match `data/study/main-v1/manifest.json`; the creation timestamp differs. The SQL command uses zero generation requests and does not reproduce the learned reader's decisions.

## Recompute results from saved model responses

Scoring uses the standard library. Figure generation adds hash-pinned dependencies:

```sh
python3 -m venv .venv-analysis
.venv-analysis/bin/python -m pip install --require-hashes -r release/requirements-analysis.lock
.venv-analysis/bin/python analysis/audit_run.py --run experiments/main/primary --data data/study/main-v1 --output reproduced-primary/provenance-audit.json
.venv-analysis/bin/python analysis/analyze_study.py --run experiments/main/primary --data data/study/main-v1 --output reproduced-primary
.venv-analysis/bin/python analysis/figures.py --analysis reproduced-primary/summary.json --output reproduced-primary/figures
.venv-analysis/bin/python analysis/audit_run.py --run experiments/main/sensitivity --data data/study/main-v1 --output reproduced-sensitivity/provenance-audit.json
.venv-analysis/bin/python analysis/analyze_study.py --run experiments/main/sensitivity --data data/study/main-v1 --output reproduced-sensitivity
.venv-analysis/bin/python analysis/figures.py --analysis reproduced-sensitivity/summary.json --output reproduced-sensitivity/figures
.venv-analysis/bin/python analysis/error_localization.py --analysis reproduced-primary --output reproduced-primary/error-localization.json
.venv-analysis/bin/python analysis/error_localization.py --analysis reproduced-sensitivity --output reproduced-sensitivity/error-localization.json
.venv-analysis/bin/python analysis/cost_accounting.py --runs experiments/main/primary experiments/main/sensitivity --output reproduced-cost-accounting.json
```

Every planned attempt remains in the denominator. The 576 primary and 192 sensitivity **logical attempts** came from 676 actual generation requests and 92 within-block reuses of responses to identical serialized requests. All attempts completed; none was truncated. Summaries separately report physical calls, reused requests, failures, tokens and timings. A reused answer is not fresh inference. Intervals resample company worlds within the three fixed fictional families, not real businesses.

This convenience command verifies archive hashes, runs tests, regenerates data, audits both ledgers, compares recomputed analysis, descriptive error reports, cost accounting and vector figures, reruns SQL and compiles the paper:

```sh
.venv-analysis/bin/python scripts/reproduce_saved.py --output reproduced-evidence
```

It requires system TeX/BibTeX, Pandoc, `pdftotext` and `pdfinfo`. The output directory must be new. Add `--fresh-smoke` only when the pinned local services below are running: that makes two actual reader calls, not a fresh main benchmark. The receipt states which checks ran. Clean extraction and an isolated Python environment do not imply independent hardware or a freshly compiled inference server.

Add `--upstream-scorer-check` to also reproduce the narrow EnterpriseMem-Bench scorer diagnostic discussed in the literature notes. It requires network access to three public GitHub files on first use, checks their pinned hashes, and makes no model calls. This reproduces constructed scorer counterexamples, not that project's model results. It can also run separately without overwriting the archived report:

```sh
python3 scripts/audit_enterprisemem_scorer.py --output reproduced-upstream-scorer/report.json
```

## Actual model inference

The main reader is pinned Qwen3-30B-A3B-Instruct-2507 Q4_K_M; the embedder is Qwen3-Embedding-0.6B Q8_0. Their Apache-2.0 weights total about 19.2 GB and are **not included**. The measured setup used four CPU threads on AMD EPYC 9V74, 32 GiB RAM and AVX512 generation/AVX2 embedding builds. Allow several CPU hours and enough disk for weights, builds and outputs. No paid API key is needed. Other hardware, compilers or weights can change outputs and latency; record the actual runtime rather than silently reusing the measured runtime metadata.

Prerequisites: Python 3.12, `uv`, C/C++ compiler, Make, a compatible CPU and network access to the pinned GitHub/Hugging Face artifacts:

```sh
bash scripts/setup_local_inference.sh
python3 scripts/download_research_model.py --moe-model
python3 scripts/download_research_model.py --embedding
```

Build the generation binary with the additional commands in `worklog/avx512-build.md`. That public recipe is included; private work logs are not. Start each service in a **separate terminal** and wait for readiness:

```sh
bash scripts/start_research_model.sh reader
```

```sh
bash scripts/start_research_model.sh embedding
```

They bind to loopback ports 8080/8081. Do not launch duplicate services or parallel benchmarks against the one-slot reader. Download scripts verify hashes; runtime manifests describe the measured build, not an automatic detector for another computer.

A small **real inference** check:

```sh
python3 -m study.run --data data/study/runtime-smoke-v1 --output new-inference-smoke --model-config experiments/qwen3-moe-study.json --runtime-manifest experiments/qwen3-moe-runtime.json --embedding-cache new-smoke-embeddings.jsonl --methods prompt_hybrid typed --conditions initial --token-cap 1024
```

A fresh execution of both frozen main blocks:

```sh
python3 scripts/run_frozen_study.py --output-root new-main
```

The driver verifies source/data/configuration hashes. It runs the 1,024-token primary block before the 1,536-token sensitivity block, without development-generation reuse. Full context has a separate 15,000-token cap. Seeds, output allowance and within-block reuse rules are in the freeze files. Temperature zero does not guarantee identical results across runtimes.

After an interruption, restore the same pinned services and use:

```sh
python3 scripts/run_frozen_study.py --output-root new-main --resume
```

An exclusive lock rejects concurrent execution. Completed/failed attempts are never repeated. Issued attempts lacking terminal responses become interrupted failures with unknown usage; only unstarted work resumes. Preserve failures instead of deleting them to improve results. Local API charges were zero; infrastructure dollars and energy were not measured.

## Compile the paper

Install system `pdflatex`, `bibtex`, `lmodern`, `microtype`, `booktabs`, `natbib`, `hyperref` and standard graphics/math packages. `pdftotext` supports the reproduction check. The measured TeX version is in `paper/report-build.json`; no hermetic operating-system image is supplied.

```sh
python3 scripts/compile_investor_note.py --output reproduced-paper/investor-note.pdf
python3 scripts/compile_paper.py --output reproduced-paper/report.pdf
```

The scripts resolve references and record source/PDF hashes. The investor note uses Pandoc and one Markdown source, with a pagebreak marker; its build enforces exactly two pages and also emits LaTeX. PDF timestamps/binary metadata can differ. Compilation is not scientific validation or visual inspection; the separate delivery record covers the rendered PDFs actually inspected.

## Evidence and rights

- `data/study/DATA_CARD.md`: fixture provenance, schema, split and limits.
- `papers/company-memory/protocol/`: prospective internal freeze, pilot, planning rule and retained amendments; not external preregistration.
- `experiments/main/` and `analysis/main/`: complete traces, manifests, source snapshots, computation receipts and paired estimates.
- `release/TUNING.md` and `experiments/pilot/`: retained failures and interface changes, not pooled main findings.
- `literature/`, `release/literature-index.json`, `sources/bibliography-audit.json`: bounded search, critical reviews, contribution/reuse decision, source versions and citation checks. Copied abstracts and paper PDFs are excluded.
- `release/THIRD_PARTY.md`: dependency attribution. MIT covers original code; CC BY 4.0 covers the explicitly included original data/output/documentation artifacts.

No customer records, private production source, credentials, weights or private planning history are distributed. AI-assisted authorship and the absence of independent human strategic assessment are disclosed. A tested package does not imply peer review, acceptance or public publication.
