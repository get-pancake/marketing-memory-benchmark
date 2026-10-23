# Integrated marketing-memory companion — v3 acceptance

Verified 23 October 2026. This accepts the completed English empirical technical report and its tested reproducible companion. The study measures evidence selection and grounded action eligibility on fictional data, with a separate exploratory raw-document/wiki track. Independent practitioner validation, commercial outcomes, public distribution, venue submission and peer review are not claimed.

## Delivered report

- **Company Memory for Grounded Marketing Recommendations: Separating Evidence Selection from Reader Performance**, `paper/report.pdf`: 13 pages including references and appendices, six vector figures and five tables. SHA-256 `49cb879bb336038bfdcb9bb085bac3768be7760b236826c4bbf0a97273f32583`.
- `paper/investor-note.pdf`: two pages, generated from its single Markdown source. SHA-256 `742f43aa58b2d56e0177e9fec89696126f36210e288254d570ea20556d3c1ebf`.
- All 15 pages visually inspected; exact render hashes and reviewer disclosure are in `release/VISUAL_INSPECTION.json`. Diagram border clipping and a paired-effect axis-label collision were corrected before final inspection. The final TeX log contains no layout or unresolved-reference warnings. This is research-assistant inspection, not independent human review.
- The numeric register verifies 853 quantities against hashed source artifacts, including explicitly historical v1/v2 claims. It verifies 31 citation keys across retained TeX sources and 35 bibliography records; the current report cites 16 works. Counts do not imply exhaustive full-text coverage or automatic validation of every prose interpretation.

## Actual experimental evidence

| Track | Completed evidence and interpretation |
| --- | --- |
| Frozen main | 33 newly generated fictional worlds, 264 cases, seven contexts and two fixed readers; 3,696 actual GPT/Claude calls, zero main technical failures |
| Context audit | 7,392 packets rebuilt from saved real embeddings/native GBrain rankings; all main raw responses rescored; frozen source and data hashes unchanged |
| Primary contrast | Both readers: Generic 223/264 versus Specialized 264/264; +15.53 percentage points, 95% family-stratified world-bootstrap interval [9.85,21.21] |
| Strong controls | Structured Markdown, GBrain plus the same coverage layer and full current context also 264/264; native GBrain search is a bounded component comparison, not a whole-product ranking |
| Retrieval sweep | At 1,024 bytes, specialized support 132/132 versus Markdown 52/132; retrieval only, with no inferred recommendation result at that allowance |
| External documents | 118 MIT-licensed development pages, actual query-blind general/marketing wiki compilations, original 220 QA calls plus 44 disclosed post-hoc chunked-control calls |
| External robustness | A stronger chunked control and one-question ambiguity sensitivity limit the apparent wiki advantage; original scores/labels remain unchanged |
| Action interface | 1,278 proposals pass a separately executed in-memory mock workflow check through 2,606 capability calls; zero external actions or commercial outcomes |
| Resources | Main usage estimate $33.9875616; known generation+embedding estimate $55.48847274 across all provider work. Three unsuccessful attempts lack usage receipts and may incur additional charges. Not invoices or full lifecycle costs |

The data generator and task families were known in development. These are fresh-world results within a formal synthetic benchmark, not unseen real-company validation. The shared current-view filter supplies temporal/access handling to every selector. Every negative main case is withheld appropriately; gains recover missing positive support. Exact SQL solves the formal task without model calls. Qualitative inspection traces three main cases and all non-no-context external failures, without claiming blinded human assessment.

The original incomplete pilot, schema failures, compilation timeouts/truncations and recovery journals remain retained. Eight complete main response/result files were reconciled after a runtime interruption; only 624 previously unissued calls resumed, with no repeated generation. Historical Qwen/GBrain studies and original v1/v2 archives remain separate from the new sample.

## Clean reproduction performed

Candidate `exports/marketing-memory-integrated-companion-v3-candidate.zip` was extracted outside the private Git tree at `/tmp/marketing-companion-clean-v3-attempt1`. A separately installed, hash-pinned Python 3.12 environment ran the documented command with inherited Python paths removed. No inherited Git tree or model service was required.

The complete run passed on its first attempt, **01:27:06–01:27:44 UTC on 23 October 2026**. Receipt: `release/reproduction-records/clean-reproduction.json`. The verified core payload SHA-256 is:

`e3f767faf190094cca840866ae685febbd346d962a11cab677c44025ccbd9476`

| Check | Recorded result |
| --- | --- |
| Package integrity | All 17,017 input payload files and the manifest verified; all remained unchanged |
| Correctness tests | 85 passed: 58 general and 27 frozen-study/analysis tests |
| Integrated data and context | Input/label bytes and all 7,392 reconstructed packets identical |
| Main statistics | All 3,696 raw scores, paired estimates, uncertainty and per-attempt records reproduced |
| External study | Original 220 raw scores, 44 chunked-control scores and label sensitivity reproduced |
| Accounting and mock execution | Usage accounting reproduced; mock workflows reexecuted with identical receipts |
| Figures and tables | All integrated and retained historical figure/table bytes regenerated identically |
| Historical evidence | Original data, analyses, GBrain saved-ranking replays and 123 external-source file hashes verified |
| Paper and investor note | Recompiled with identical extracted text/layout; investor LaTeX identical and exactly two pages |
| Fresh provider calls | Zero; saved-output reproduction is not fresh inference |

This verifies a clean extracted install and saved-output reproduction on the same host with system TeX/Pandoc/Poppler. It does not rerun native GBrain search, embeddings or model inference and is not independent-hardware replication. PDF binary metadata may differ; delivered originals are identified by the hashes above. The 34 executed command logs, environment installation receipt and regenerated evidence are retained. Prior passing v2 records were moved intact to `release/reproduction-records/v2-passed/`; earlier failures and v1 records remain.

After extracting the final archive and installing dependencies from its README:

```sh
python scripts/reproduce_saved.py --output NEW_REPRODUCTION_DIRECTORY
```

Fresh reader inference, native retrieval, embedding acquisition and wiki compilation have separate documented commands and resource requirements.

## Revision and release boundary

Main design/code freeze: `61c57c67c1bb4d356ce5ea38672c522df6958138`. Completed experiment/manuscript implementation was committed and pushed privately at `ed8c45de` (the final archive manifest records the full delivery revision). The final build requires a passing clean-reproduction receipt for the exact core above. Reproduction records and this acceptance narrative are excluded only from that core digest to avoid a circular reference; they remain individually hashed in the final manifest.

Original code is MIT; specified original data, outputs and documentation are CC BY 4.0. External development documents retain upstream MIT/credits. Proprietary model services are not licensed by the package. The public allowlist excludes private planning/source-review pointers, credentials, customer data, model weights and third-party paper PDFs.

The working repository remains private. **The companion is tested and ready for a separate public release; no public distribution or paper submission has occurred.** Use the exact final manifest and hashes rather than a candidate filename to identify the accepted package.
