# Empirical companion acceptance record

Completed 22 October 2026. This record accepts the **controlled verified-event technical report and its companion**, not a production system, independently validated commercial strategy, peer-reviewed paper or public publication.

## Delivered evidence

- English report: `paper/report.pdf`, 18 pages including references and appendices. SHA-256: `b07c17a21f9ec6771df2decd740e4db25f48fd9edb5626b9e28b24d4d1302635`.
- Investor note: `paper/investor-note.pdf`, exactly two pages, with the same findings and limits. SHA-256: `58158a708a48717b4e8696f1e49fa7853e20be2de0950ed68a610c831615f58e`.
- All 20 delivered pages visually inspected; exact PDF and rendered-page hashes, scope and reviewer disclosure are in `release/VISUAL_INSPECTION.json`. No final TeX layout or unresolved-reference warnings remain.
- Bounded critical review: 399 unique search records, 32 metadata-verified bibliography entries, detailed nearest-work notes, artifact/license inspections, contribution/reuse memo and explicit coverage/access limits. The paper cites 24 verified keys. This is not a claim to have read every candidate or reproduced author model results.
- Frozen primary and sensitivity studies: 576 + 192 logical attempts across 12 fictional worlds, 676 physical generation requests and 92 identical-request reuses. Both ledgers and provenance audits are complete; no failed, truncated, missing or schema-invalid main response was dropped.
- Original unsuccessful development runs, all main raw responses, source bindings, source snapshots, model/runtime pins, source/data hashes, paired-world intervals, descriptive errors and computation accounting are retained.
- The public numerical register has 148 quantities checked against hashed source artifacts. This is not automated scientific validation of the prose.

The primary result is deliberately mixed: catalog coverage scores 53/96 versus 40/96 for prompt hybrid, with a paired difference of 13.5 percentage points and a world-bootstrap interval of [0.0, 28.1]. The primary interval includes zero. Complete positive support availability does not establish reliable decisions: catalog coverage succeeds on 21/48 positive queries and recommends inappropriately on 16/48 negative queries. The larger-budget comparison is exploratory. SQL solves the known formal rules directly. The manuscript and investor note make no revenue, retention, network-effect, graph-superiority or production-readiness claim.

## Executed clean reproduction

The first complete candidate was extracted outside the private Git tree and tested in a separately created Python 3.12.14 virtual environment with hash-pinned dependencies. No inherited Git repository or Python import path was used. The clean check ran from **12:53:51 to 12:55:22 UTC** and passed on its first execution.

Receipt: `release/reproduction-records/clean-reproduction.json`. Verified core payload SHA-256: `5a0d0b5829928ee532a9d012909bc287490092a4f5e830d4da3e99f2a0f15718`.

| Check | Recorded outcome |
|---|---|
| Offline correctness and provenance | 59 tests passed: 32 original and 27 study/analysis checks |
| Main fixture regeneration | Input and label files byte-identical |
| Input/output capacity diagnostics | Saved tokenizer receipts verified offline |
| Both provenance audits and analyses | Same scores, planned denominators and paired estimates; per-attempt/audit bytes identical |
| Error localization and computation | Identical apart from documented timestamps/paths |
| Vector figures and tables | Regenerated PDF, SVG and table bytes identical |
| Exact SQL reference | All outputs identical excluding measured timing |
| Claims and bibliography | 148 registered quantities and all cited keys verified |
| Manuscript and investor note | Compiled again; extracted text/layout identical; investor LaTeX identical and two pages |
| Upstream scorer diagnostic | Three public pinned/hash-checked files downloaded; constructed counterexamples reproduced, zero model calls |
| Fresh model execution | Two new reader requests completed and audited, zero response reuse; raw traces retained |
| Artifact integrity | Every original packaged file and manifest remained unchanged after reproduction |

The fresh requests establish execution and provenance, not a new main accuracy estimate. The full main inference was **not** rerun. Reproduction used the same host, system TeX and existing pinned inference services, not independent hardware or a newly compiled inference runtime. Binary PDF metadata can differ; the delivered PDF hashes above identify the visually inspected originals. These limits are encoded in the receipt rather than inferred from a successful exit code.

From a fresh extraction with the pinned dependencies and services described in `release/README.md`, the tested command is:

```sh
python scripts/reproduce_saved.py --output new-reproduction --fresh-smoke --upstream-scorer-check
```

Use a new output directory. Omit the two optional flags for saved-output reproduction without fresh model requests or upstream downloads. A full new model benchmark is the separate `scripts/run_frozen_study.py --output-root new-main` command and requires the documented resources.

## Release boundary

The companion explicitly includes original code, licensed fictional data, releasable outputs, protocols, review notes, analysis, figures and document sources. It excludes private planning/source-review history, customer data, credentials, third-party PDFs, model weights and source caches. Code uses MIT; the specified original data/output/documentation artifacts use CC BY 4.0. External dependencies retain their own licenses and attribution.

The frozen experimental revision is `eeede44635c996216a1d8e6e930e6f8df321b1c2`. The final archive records its working revision and every file hash in `MANIFEST.json`. Acceptance and reproduction receipts are excluded only from the core-payload digest to avoid a circular self-reference; they are still individually hashed in the final manifest. The final builder requires a passing receipt for the exact core payload.

The working repository remains private. The tested companion is prepared for public release; **public distribution and paper submission have not occurred**. Independent human GTM assessment, raw-document ingestion experiments, fresh full-main reproduction and commercial-outcome validation remain separate research or release milestones, not completed claims.
