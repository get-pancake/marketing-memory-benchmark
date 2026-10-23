# Reproduction guide

Reproducible companion to an English empirical industrial technical report, 23 October 2026. The main experiment holds the reader fixed while changing its context: **no company context, general company context, and GTM context**. The new readers are actual **Claude Opus 5.5** and **GPT-6.1 Sol**. The frozen main contains 120 original fictional company worlds, 360 multi-account cases and 4,320 reader attempts. Full context, structured Markdown, native GBrain search and a generic query-word control remain visible.

The primary score is grounded feasible policy value relative to a formal optimum. It is neither revenue nor human-rated strategic usefulness. The generic query-word control produces exactly the GTM inputs; its aliased scores are not additional model observations. The main task starts from verified structured events. A separate 132-call Opus extension evaluates raw documents and query-blind generic/marketing wikis on 22 development questions from one externally authored fictional company. That small track does not establish a universal specialized-memory advantage.

Read `paper/report.pdf`, the two-page `paper/investor-note.pdf`, `release/ACCEPTANCE.md` and the exact clean-reproduction receipt. `MANIFEST.json` hashes every public payload. Packaging does not publish the private working repository or submit the paper. Historical experiments, PDFs and unsuccessful attempts remain separate and are not pooled into the new sample.

## Compared implementations

| Context | Implementation and boundary |
| --- | --- |
| None | Same task/catalog without company evidence; information reference |
| Company | Native pinned GBrain ranking plus domain-neutral entity/link closure |
| GTM | Same ranking/packer with catalog-required relation closure |
| Company + query words | Generic relation-name filtering from the shared query; audited identical-input control, no extra inference |
| Markdown | Original lossless entity wiki, BM25/real-dense rank fusion and generic closure |
| GBrain search | Native PGLite/balanced hybrid entry point and bounded packing alone |
| Full current context | Every current permitted record; larger information and cost reference |

Evidence allowances are 16/12/8 KiB for the three compound stress levels, measured in UTF-8 bytes rather than model tokens. Provider token usage is retained. Native GBrain is a search component, not a whole-product or hosted-service evaluation: the long composite query produced no lexical matches in this configuration, and expansion/reranking are disabled. All closure methods share its ranking. The Markdown arm is not an official Karpathy product or a model-written wiki. The external track does use actual query-blind LLM compilation, inspired by the Markdown/wiki pattern, with no claim of endorsement.

## Install and inexpensive checks

Python 3.12; scoring/tests use the standard library, and statistical analysis/figures use hash-pinned NumPy/Matplotlib. PDF builds additionally require system LaTeX/BibTeX, Pandoc and Poppler. Exact observed versions are in build receipts.

```sh
python3 -m venv .venv-analysis
.venv-analysis/bin/python -m pip install --require-hashes -r release/requirements-analysis.lock
.venv-analysis/bin/python -m unittest discover -s tests -v
.venv-analysis/bin/python -m unittest study.test_contract study.test_ledger analysis.test_analysis analysis.test_audit -v
.venv-analysis/bin/python -m benchmarks.challenge.check_oracle --data data/challenge/main-v1 --output oracle-check.json
```

These checks make zero API calls. An independent SQLite eligibility implementation and exhaustive optimizer verify the formal labels; they are not human or independent-author validation.

## Recompute saved evidence without credentials

Use new output paths. Every context packet is reconstructed, every raw response rescored, and all attempts remain in the denominator.

```sh
.venv-analysis/bin/python analysis/challenge_audit.py --data data/challenge/main-v1 --packets experiments/challenge/main-context-v1 --output reproduced-context-audit.json
.venv-analysis/bin/python analysis/challenge_trace_audit.py --data data/challenge/main-v1 --packets experiments/challenge/main-context-v1 --run experiments/challenge/main-reader-v1 --freeze experiments/challenge/main-freeze-v1.json --output reproduced-trace-audit.json
.venv-analysis/bin/python -m benchmarks.challenge.analyze --data data/challenge/main-v1 --packets experiments/challenge/main-context-v1 --run experiments/challenge/main-reader-v1 --output reproduced-main
.venv-analysis/bin/python analysis/challenge_budget.py --data data/challenge/main-v1 --packets experiments/challenge/main-context-v1 --output reproduced-budget.json
.venv-analysis/bin/python analysis/challenge_figures.py --summary reproduced-main/summary.json --budget reproduced-budget.json --external analysis/challenge/external-opus/summary.json --output reproduced-figures
.venv-analysis/bin/python analysis/challenge_external_opus.py --analyze experiments/challenge/external-opus-v1 --output reproduced-external-opus
.venv-analysis/bin/python analysis/challenge_accounting.py --output reproduced-accounting.json
.venv-analysis/bin/python scripts/verify_report_claims.py
```

The primary unit is a company mean over positive cases. Bootstrap intervals resample companies, not individual calls, within administrative sector strata. Negative-case safety has a separate denominator. The wider-budget sweep reruns retrieval only; it does not create reader performance measurements at those budgets. The `precision_rule` field produced by the shared analyzer is a run-specific diagnostic; only the original development pilot selected the sample, as documented in amendment 02.

## Fresh paid readers and native retrieval

Read `papers/company-memory/protocol/challenge-v1.md`, both amendments and `benchmarks/challenge/providers.json`. Check current availability, prices, quotas and your own spending limits. Supply your own `RESEARCH_OPENAI_API_KEY` and `RESEARCH_ANTHROPIC_API_KEY` through the environment or a secret manager. No credentials are included. Planning is offline; `--execute` issues paid requests. The numerical cap below is the recorded researcher operational guard, not a forecast or an authorization for a new operator.

```sh
python3 -m benchmarks.challenge.run --config benchmarks/challenge/providers.json --data data/challenge/main-v1 --packets experiments/challenge/main-context-v1 --output fresh-plan
python3 -m benchmarks.challenge.run --config benchmarks/challenge/providers.json --data data/challenge/main-v1 --packets experiments/challenge/main-context-v1 --output fresh-readers --execute --operational-cap-usd 1500 --workers 16
```

These commands use the saved input packets. To rerun native search, first install the pinned GBrain/Bun dependencies documented in `benchmarks/gbrain/README.md`. The challenge uses actual OpenAI vectors and does not need the historical local Qwen runtime. The snapshot is losslessly sharded to keep files within ordinary Git sizes; its original monolithic filename is a logical reference, not a missing dependency.

```sh
python3 scripts/hydrate_challenge_cache.py --snapshot experiments/challenge/main-context-v1/embedding-snapshot.json.gz --output fresh-embedding-cache.sqlite
python3 -m benchmarks.challenge.prepare --data data/challenge/main-v1 --output fresh-contexts --cache fresh-embedding-cache.sqlite --workers 2
```

For new embeddings, use an empty cache and add `--execute-embeddings`; this sends paid OpenAI embedding requests under the frozen implementation’s $5 conservative embedding guard. A complete hydrated cache requires no provider calls. The native adapter strips provider keys from its subprocess environment. Fresh inference can be stochastic or become unavailable; saved-output reproduction and fresh inference are different claims.

The external Opus extension can separately be rerun with `analysis/challenge_external_opus.py --output fresh-external-opus --execute --operational-cap-usd 175`. It reuses the exact existing external contexts. Original wiki compilation and historical GPT/Sonnet evaluation are documented in `release/history/v3/release/README.md`; changed reader effort settings prevent a clean model-only comparison with those historical numbers.

## Compile and verify the complete extracted package

```sh
.venv-analysis/bin/python scripts/compile_investor_note.py --output rebuilt/investor-note.pdf
.venv-analysis/bin/python scripts/compile_paper.py --output rebuilt/report.pdf
.venv-analysis/bin/python scripts/reproduce_saved.py --output clean-reproduction
```

The final command requires an extracted archive with `MANIFEST.json`. It verifies all public hashes, runs tests, regenerates datasets, reconstructs contexts, rescores raw responses, recomputes statistics/costs/figures, and recompiles the paper and investor note. It also verifies retained historical evidence. No fresh API calls are made. The acceptance receipt states the exact scope: isolated extracted files and Python environment on the same host, with system TeX, rather than independent-hardware replication.

## Evidence and licensing

- `experiments/challenge/main-freeze-v1.json`: code/data/input freeze; `main-reader-v1/`: all requests, responses, usage, timings and terminal ledger entries.
- `analysis/challenge/`: raw-response analysis, independent oracle, context/trace audits, budget sweep, qualitative examples and accounting.
- `data/challenge/DATA_CARD.md`: original generator, provenance, labels, dependence and known construction shortcuts.
- `literature/`: bounded search record, critical reviews and reuse decisions. The bibliography audit distinguishes verified metadata from review depth.
- `release/CLAIMS.json`: numeric claims with source hashes/key paths; `THIRD_PARTY.md`: upstream revisions/licenses and exclusions.

Original code is MIT; specified original data and documentation are CC BY 4.0. Externally authored company documents retain upstream MIT and credits. GBrain is separately installed under MIT. Provider models/services are not licensed by this package. Model-generated outputs are identified as such, not human ground truth. No production code, customer records, private planning history, credentials, model weights or third-party paper PDFs are included.

A recorded three-case native replay also hydrates a new cache and creates new PGLite instances from released vectors:

```sh
python3 scripts/replay_challenge_native.py --output native-replay-new --receipt native-replay-new-receipt.json
```

The original replay matched all native GBrain rankings and 18 context packets. Two auxiliary Markdown full rankings differed at floating-point near-ties; their selected packets did not change. That fresh-run stability limit and both checker failures are retained. No new provider requests were required. The complete cached-analysis reproduction relies on the recorded original rankings, not an assumption of fresh ranking determinism.
