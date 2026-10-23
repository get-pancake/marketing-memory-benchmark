# Preliminary marketing-memory companion — v2 acceptance

Verified 22 October 2026. This record accepts the revised **preliminary controlled component report and its reproducible companion**. The broader two-paper research program, frontier-provider comparison, independent practitioner validation, public distribution and submission remain incomplete. See `release/PUBLICATION_STATUS.md` for those gates.

## Delivered report and evidence

- `paper/report.pdf`: **Evidence Selection in B2B Marketing Memory: A Preliminary Component Study**, 19 pages including references and appendices. SHA-256 `e56b0f34964fc346396d84301d0e8574b73a89a2c2279e84f12d86ba23bc3d19`.
- `paper/investor-note.pdf`: two pages. SHA-256 `1fbbd0d1421573481d964716013eaba3103f551f4e79ab89cb9705c6b9fb8cce`.
- All 21 pages visually inspected; exact rendered-page hashes and assistant-review disclosure are in `release/VISUAL_INSPECTION.json`. The final TeX log has no layout or unresolved-reference warnings. This is not independent human review.
- Original v1 experiment sources and outputs remain unchanged: 768 logical attempts, 676 physical reader requests, 92 identical-request reuses, 12 fictional worlds. The primary decision interval includes zero. Complete positive support does not make the reader reliable.
- Actual GBrain hybrid component at upstream revision `531b3b1ab66c88f192abb51338028c44b80fbf21`: 96 completed native searches in `experiments/gbrain/exploratory-96-v2`. The adapter uses identical permitted verified facts and actual recorded embeddings. Raw ingestion, graph extraction, paid reranking and whole-product behavior are excluded. Development and integration failures are preserved separately.
- Canonical exploratory context analyses at 1,024, 1,536 and 4,096 tokens are under `analysis/gbrain/reproducible-*`. The same catalog-coverage module on GBrain matches the specialized selector; every tested method supplies complete positive support at the largest allowance. No recommendation or commercial outcome is inferred from these context scores.
- `analysis/context-v1/` separates evidence availability from the original reader responses; this is a post-hoc diagnostic, not a new primary endpoint.
- The prospective Claude/GPT pilot has 64 prepared physical requests and equal context within each case. No provider experiment has run. Offline plans and tests are not model outcomes. Public data from an external project are licensed and verified, but downloading them is not an ingestion experiment or independent human validation.
- The claim register verifies 223 quantities against saved artifacts; 24 cited keys and 32 bibliography entries have metadata verification. The bounded literature search contains 399 unique arXiv candidates, with review depths and limitations disclosed separately from the additional GBrain source review. This is not exhaustive full-text coverage.

## Clean reproduction

The corrected candidate was extracted outside the private Git tree at `/tmp/marketing-companion-clean-v2-attempt2`. A separately created Python 3.12 environment installed hash-pinned dependencies. No inherited Git repository or Python import path was used. Both local model services were stopped before verification.

The passing run took place from **22:12:58 to 22:13:15 UTC**. Receipt: `release/reproduction-records/clean-reproduction.json`. Verified core payload SHA-256: `fbc9758b9f8607413402e902fef5566c1bf17d311a085cfb6ed0df8b698a4ec3`.

| Check | Recorded result |
| --- | --- |
| Unit, adversarial and provenance checks | 69 passed: 42 general/new benchmark checks and 27 frozen-study/analysis checks |
| Main fixture and original analyses | Input/label bytes, paired estimates, audit records and figures reproduced |
| Context/reader decomposition | Identical apart from creation timestamp |
| GBrain saved-ranking replay | All three budgets, selected-source rows, token receipts and generated table identical |
| External development data | All 123 retained upstream files verified against hashes and sizes |
| Claude/GPT preparation | Same 64-request plan regenerated; zero provider requests |
| SQL, costs and capacity checks | Reproduced, with timing excluded only where specified |
| Numerical and citation register | 223 quantities and all cited keys verified |
| Report and investor note | Recompiled; extracted text/layout identical; investor LaTeX identical and exactly two pages |
| Package integrity | All 1,051 input payload files and the manifest remained unchanged |

The first attempt failed in the offline token-receipt closure at 1,536 tokens. Its receipt/logs are retained under `release/reproduction-records/v2-attempt1/`. The correction changes the analysis-script hash, not rankings, selected evidence, token counts or scores. Previous analysis bytes remain under `analysis/gbrain/pre-offline-fix-*`. A regression test prohibits network requests while replaying all controls. The corrected full clean run passed; the failure is not erased.

This verifies **saved-output reproduction on the same host**, with system TeX/Pandoc/Poppler. It does not rerun native GBrain, embeddings, full main inference or any frontier provider, and does not establish independent-hardware reproduction. Original v1 fresh-model and upstream-scorer checks are retained as historical evidence under `release/reproduction-records/v1/`; they are not claimed as newly executed v2 checks. Binary PDF metadata can differ; the visually inspected delivered hashes above identify the final originals.

After extraction and dependency installation from `release/README.md`, the verified command is:

```sh
python scripts/reproduce_saved.py --output new-reproduction-directory
```

Fresh model inference, native GBrain execution and the prospective provider benchmark have separate documented commands and resource requirements. A saved-output check is not a fresh model benchmark.

## Release boundary

Original code is MIT; specified original data, outputs and documentation are CC BY 4.0. Included external development material retains upstream MIT and credits. The allowlist excludes private planning/source-review pointers, credentials, customer data, model weights and third-party PDFs. The original v1 report and receipts are preserved under `release/history/v1/`, with its original release archive retained separately.

The final archive manifest records the exact working revision and every included file hash. Reproduction records and this acceptance narrative are excluded only from the core digest to avoid a circular reference; they remain individually hashed. The builder rejects a final package without a passing receipt for that exact core. The working repository remains private. **The companion is prepared for public release; it has not been publicly distributed or submitted.**
