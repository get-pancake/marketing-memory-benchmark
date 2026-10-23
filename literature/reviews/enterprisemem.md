# EnterpriseMem-Bench: critical artifact review

Review date: 2026-10-21 (America/Los_Angeles). Primary artifact: [repository](https://github.com/enterprisemem-bench/enterprisemem-bench/tree/819a8bc99db576a21828c2a8e6d273ae2ff023c4), revision `819a8bc99db576a21828c2a8e6d273ae2ff023c4`.

**Depth:** entire released `paper.tex`, README, bibliography, data license, four evaluation modules, and the ten-question fixture/answer subset read. The PDF layout, generation pipeline, full dataset, memory adapters and model traces have not been reproduced. Source bytes and hashes are in `../retrievals.jsonl`; downloaded texts are private reading-cache material.

## Metadata and contribution

The manuscript identifies Xiwei Zhou as author and uses the title *EnterpriseMem-Bench: Fair Benchmarking of Long-Horizon Enterprise Memory Systems*. The repository identifies it as a 2026 preprint and supplies DOI `10.5281/zenodo.20199468`. DOI registration and a peer-reviewed venue have not been independently checked. A conference-style template is not evidence of acceptance.

The task is finance question answering over one fictional company's changing record. The design section describes 100 sessions, 200 questions, four levels (direct recall, cross-session retention, updates/retirements and synthesis), and a canonical fact timeline. These are source-reported corpus properties, not independent audit counts for the full corpus.

The most useful mechanism is causal evaluation: each question sees the state at its own session cutoff rather than a store containing the entire future. The comparison fixes the answer model and question-time retrieval for mutable systems while allowing native ingestion to differ. It separates memory-side misses from answer-side failures and includes full-context and no-context references. We should reuse these principles rather than claim them as new.

## Baselines and accounting, as reported

`paper.tex`, Evaluation Setup, describes GPT-4.1 as reader; native Mem0/LangMem ingestion uses GPT-5.4-mini and text-embedding-3-large. Shared retrieval uses three query variants, overfetch, deduplication, a similarity threshold and recency as a secondary rank key. A separate transcript RAG uses eight session chunks. The mutable pipelines therefore do not isolate every factor against the transcript baseline. The costs discussion excludes setup/ingestion tokens and reports single-run answer-side telemetry; it cannot establish comparable *total* cost for our hypothesis.

The paper's question-level Wilson intervals describe uncertainty over that item set. Two hundred questions from one company are not two hundred independently sampled organizations. Its claim that the same failure pattern transfers to other verticals remains a hypothesis; the limitations acknowledge that a second domain was not evaluated.

The full-context configuration is an informative control, not a mathematical upper bound and not intrinsically unsuitable for small records. We must measure its quality and total resource use instead of dismissing it.

## Reproducibility and consistency limits

- The current README explicitly says adapters and raw result files are absent. The manuscript appendix says result files are archived in the repository. Use the actual release's availability statement; do not label the system comparison reproduced.
- The README warns that the manuscript predates a number audit. Several narrative statements are not reconciled with tables: for example, the robustness section says all five configurations were rerun but its table explicitly excludes CausalRAG. Its unrun performance cannot be inferred from another model's ceiling gap.
- The limitations identify the two taxonomy annotators as the author and DeepSeek-V4-Pro. This is human–model agreement, not two independent human assessors.
- The ten-question answer subset has empty `sql_query` fields. A claim of SQL provenance in the release description is not a per-row executable provenance chain in this inspected subset.
- Code is MIT; data is CC BY 4.0, explicitly distinguished by `LICENSE-DATA`. The manuscript appendix's single-license wording is less precise. Retain separate attribution if any data/code is reused.

## Executed scorer diagnostics

Reproduction command: `python3 scripts/audit_enterprisemem_scorer.py --output reproduced-upstream-scorer/report.json` from the repository root. Archived evidence: `literature/diagnostics/enterprisemem-scorer.json`. This downloads only hash-checked, inspected source at the fixed revision if the cache is absent. It makes no model calls. The output must be new; download receipts stay beside it so reproduction does not overwrite the historical evidence. The CLI was updated for packaging on 22 October; its unchanged probes reproduced every archived result apart from the creation timestamp.

The scorer correctly accepts the exact numeric control and rejects an incorrect numeric control. It also accepts the following constructed incorrect answers:

1. An answer that explicitly negates the expected budget while choosing a different value, because it accepts any matching number in the response.
2. A billion/million unit mismatch, because units are stripped without normalization.
3. A categorical answer that quotes and explicitly rejects the expected phrase, because phrase occurrence is sufficient.

In a separate omission probe using the released ten-item subset, submitting only one correct answer among five L2 questions yields KAR 1.0 with denominator 1. The top-level overall score uses all selected questions and penalizes missing answers, so do not generalize this denominator problem to every metric.

These are narrow constructed counterexamples, not an estimate of real error frequency, evidence of deliberate exploitation, or a reanalysis of unavailable model outputs. They are sufficient reasons not to copy the scorer unchanged.

## Relation and reuse decision

Already solved here: causally bounded enterprise-memory evaluation, programmatic truth, lifecycle events, shared answer conditions, and diagnostic separation of memory and answer errors. Our work cannot claim novelty in those mechanisms.

Not established by the inspected artifact: evidence-grounded Play recommendation, multiple acceptable actions, permission continuity, policy-authority distinctions, recommendation revisions and executable prerequisites, or GTM specialization beyond a prompt under total-cost accounting.

**Provisional decision:** adopt its causal-evaluation and diagnostic design principles with citation. Do not use its finance answers as GTM ground truth, copy its scorer, reproduce its performance numbers as our evidence, or choose it as the sole benchmark. A decision-support extension may still be valuable, but the contribution is conditional on reading RAMP and the other closest work.
