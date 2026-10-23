# Scoring and evidence audit

## Current multi-account challenge (v4)

The frozen `benchmarks/challenge/core.py` derives current eligible actions from the full permitted source bank. A selected context has a separately computed maximum feasible policy value. Each returned plan must satisfy eligibility, citations, one action per account, at most three accounts and the shared cost budget. Any violation invalidates the plan’s primary value. The scorer records valid action components as a separate diagnostic. Equivalent duplicate evidence sources are acceptable. All required source groups must be cited, and no citation can name an unsupplied source. Extra supplied citations are allowed by the scorer, so the metric establishes required-source completeness, not citation minimality or free-text entailment.

Positive primary value is the grounded returned value divided by the full-information optimum. Zero-optimum cases are excluded only from this explicitly defined positive denominator and retained in separate safety outcomes. A model abstaining everywhere receives zero positive value. No-context zero is expected under an evidence-required contract, not a finding that a model has no general marketing skill. Policies and utility multipliers are constructed assumptions. The exact deterministic optimizer solves the formal clean-fact task without a language model.

A separately implemented SQLite boundary/eligibility query and exhaustive enumeration agree with every main label. Both were authored in the same AI-assisted research process; no independent human review is claimed. `challenge_audit.py` reconstructs every packet and verifies byte allowance, source scope and exact query-word/GTM input equality. `challenge_trace_audit.py` checks frozen hashes, all declared requests, exact model IDs, unique response IDs and all terminal attempts. `benchmarks.challenge.analyze` redecodes every raw response and independently reconstructs its saved score and list-price usage estimate. Its frozen `precision_rule` object is calculated for whichever run is analyzed, despite the legacy `pilot_max_world_sd` field name: the main object is diagnostic only. The prospective sample decision is exclusively the original pilot plus amendment 02; main outcomes did not resize the sample.

Worlds, not calls, are resampled. Three sector labels are administrative strata of one generator, not independent held-out task families. Stress levels combine account count, distractors/conflicts and context allowance; separate factor effects are not identified. Context/reader decompositions and budget curves are descriptive. Exact query-word input equivalence does not add independent calls or establish general equivalence outside this generator.

The external extension uses upstream development answer labels and a disclosed ambiguous-question sensitivity. Citation-ID validity is checked but semantic entailment is not graded. The five non-no-context errors are preserved for qualitative review; the authorship of that review is the research assistant, not a blinded practitioner panel. API cost figures cover observed usage at recorded rates, not invoices, curation, maintenance, taxes or hardware.

## Retained historical v1/v2 audit

# What the scorer establishes

Source audit performed during frozen main inference, before inspecting main quality outcomes. This is the research assistant's code audit, not an independent reviewer or a formal proof. The 13 frozen source hashes were unchanged. Existing adversarial, accounting and recovery checks accompany the code; no newly authored model response is treated as evidence.

## Reader boundary

`study.run` passes only the query, public catalog and selected event records to `study.retrieval.messages`. Condition labels, acceptable answers and family labels are stored in the evaluator trace, outside the request messages. The query's business objective is public task input. Time/access filtering precedes retrieval. The world ID is omitted from reader messages; names, source labels and dates are task data. `analysis/audit_run.py` independently checks the saved request's query/catalog membership, evidence eligibility and exact serialized request hash.

All adapters receive already typed facts and a common easy seller/account scope. Every hybrid query includes the same public prerequisite vocabulary for templates matching the objective and resource allowance. Catalog coverage changes priority among entity/relation/authority groups; it does not consult expected alternatives, require values inferred from labels, or remove an inconvenient catalog alternative. Facet hybrid provides a domain-neutral grouping control. The generic prompt is shorter and can therefore fit more evidence under a common total-input cap.

The response grammar includes every catalog template and every supplied source label. It prevents nonexistent identifiers by construction, but permits a label in the wrong prerequisite row. The source-binding scorer must detect that error. Grammar bytes are part of the retained API request; the reported input-token allowance refers to the actual serialized chat input counted by the runtime, not a claim that constrained-decoding grammar construction is free or equal-sized. Elapsed request time includes server work.

An additional input-only audit, before inspecting main outcomes, constructs one complete minimal-slot witness for every positive query and records actual chat-template/tokenizer responses. All 48 fit the primary cap; the largest uses 951 input tokens with the shared checklist (882 with the shorter generic prompt). The diagnostic makes zero generation calls and reads no experimental ledger or hidden label file. It establishes possible evidence capacity, not retrieval/model success or an optimal context algorithm. Saved metadata responses and offline verification code are in `analysis/diagnostics/input-capacity.json` and `analysis/input_capacity.py`. This post-freeze audit did not change methods, data, cap, outcome definitions or the analysis plan.

## Truth, support and abstention

The construction labels are cross-checked against `contract.applicable(contract.visible(...))` and a separate SQLite implementation. During scoring, the complete permitted current view determines which templates actually apply. Removing evidence from the reader does not make an answerable task a correct abstention.

A positive success requires an applicable template, no source outside the supplied view, no obsolete/ineligible source, at least one current source for every required slot, no irrelevant citation, and correct per-slot source bindings. Equivalent duplicate sources may supply the same slot. Citation-set deduplication does not erase the original row bindings; swapped bindings still fail. The materializer never supplies a missing witness. Complete support can be available while the reader still fails to use it.

A negative success requires a well-formed withholding decision and no applicable alternative in the complete permitted current view. The support table and free-text missing-evidence explanation are not semantically graded for a withheld answer. Consequently, a correct negative decision may have an incorrect explanation. Always withholding scores 50% on the balanced main set. Coverage and raw recommendations on negative cases must accompany aggregate accuracy.

Every planned logical attempt stays in the denominator. Parse/shape/transport/interruption errors are not silently dropped or repaired. An issued request without a terminal record retains unknown usage; absence of a receipt is not zero cost. Identical-request reuse retains an actual origin response, including wrong/truncated outputs, and is separately counted from fresh generation. The frozen analyzer re-scores recorded answers and rejects disagreement with saved scores.

Timing clarification: all `generation_seconds`, `physical_generation_seconds`, retrieval and embedding duration fields use elapsed `time.perf_counter()` measurements. The historical manifest phrase “Local CPU seconds” means measurements on a CPU runtime; it is **not** summed process CPU time across the four threads. The report uses elapsed seconds. Do not add embedding-origin times to retrieval elapsed totals as though they were disjoint: embedding work occurs inside retrieval. Do not sum each block's unique-origin embedding totals without deduplicating origins shared across blocks. Tokens, elapsed timing, infrastructure money and energy remain distinct quantities.

## Execution and scope

Only a supported proposal is expanded into the catalog's fixed specification. `dryrun.execute` performs research-account lookup, prerequisite checks and evidence-report construction against permitted fictional records, retaining hashed receipts and one artificial unit per step. It does not call production, send outreach or optimize a workflow. It receives the complete permitted provider view after scoring; that view cannot repair the model decision. Mock completion is largely dependent on the same formal contract, not independent validation of commercial feasibility.

The SQL reference solves eligibility directly on verified facts and has zero generation calls. Its input is assumed to satisfy the dataset's event-integrity checks. It is not a replacement for adversarial raw-data ingestion or a security audit. Both independent implementations were authored within the same research process; shared conceptual mistakes remain possible. The study validates behavior under its explicit contract, not the contract's strategic wisdom.

## Response capacity, checked before outcome inspection

The output-only companion diagnostic constructs a contract-correct response for every main query and retains tokenizer responses. All 96 fit the 280-token output allowance, including one end token; maximum 127 compact or 170 indented. It reads public inputs, not labels or experimental ledgers, and makes zero generation calls. This is an existence/capacity check, not reader accuracy, a new method, or a guarantee for every possible serialization. Offline verification: `python3 analysis/output_capacity.py --verify-saved analysis/diagnostics/output-capacity.json`.

## Shared computation accounting

`analysis/cost_accounting.py` was added before inspecting main outcomes and checked on retained Stage B/cache-smoke ledgers. It deduplicates embedding origins across blocks, preserves warm-cache origin costs, and separates physical generation from logical method charges. Observed embedding time is nested inside retrieval, so it is not added twice. An estimated per-method component total combines charged generation, non-embedding retrieval overhead and one charge per associated embedding origin. This is a shared-execution accounting estimate, not a measured standalone deployment. Failed attempts lacking receipts/usage remain explicit unknowns. No natural-language extraction, human-curation cost, hardware price or energy is inferred.

## Exact prompt and request reconstruction

The provenance auditor now reconstructs each saved prompt from the permitted source events and public catalog, validates source aliases and output grammar, and compares the exact serialized request with recorded decoding settings and schema order. It rejects duplicate physical-call starts. Four additional offline tests use copies of the actual cache-smoke trace: unchanged evidence passes; rehashed forged facts, rehashed sampler changes and duplicate call starts fail. They make no model calls. This supplements the original 55 checks; all 59 are included in clean reproduction. The auditor requires matching archived serializer sources; older development audits remain historical artifacts, not silently reinterpreted as current-producer audits.

## Interpreting the working-tree flag

The run manifest records Git status after creating its output directory and source snapshot. The `working_tree_dirty` flag covers the whole working tree, including those new artifacts and documentation, rather than identifying a changed inference implementation. The experimental freeze is checked separately against the 13 producer/scorer/analysis file hashes, dataset hashes and recorded configuration. Compare those hashes with the frozen revision and saved snapshots when assessing whether the experiment changed.

## 2026-10-22T09:02:55.362521+00:00: descriptive error localization before main outcome inspection

Added `analysis/error_localization.py` as a reporting diagnostic, without changing frozen inference, scoring, analysis or primary comparisons. It preserves all planned denominators and separates positive cases by complete-witness availability and reader/output failures. The exclusive categories prioritize terminal failures before missing support; the full availability/correctness cross-tab remains visible. These are descriptive categories, not causal mediation estimates or new hypothesis tests. Every paired disagreement is retained. Illustrative trace pointers use the first lexicographic case ID within each category, rather than selection after inspecting main outcomes.

The diagnostic ran against the saved 48-attempt Stage B analysis, retaining that analysis's historical diagnostic taxonomy and primary successes. Assertions verify category totals, possible support/correctness combinations, unique method/case pairs and agreement with the original paired effect. Main results remain uninspected. The queued finalizer predates this addition: after both blocks finish, run the diagnostic separately on each complete main analysis, alongside the separate cost-accounting step. Clean reproduction must regenerate its outputs exactly apart from the creation timestamp.

## Final artifact integrity

The empirical package gate verifies completion of the evidence build, PDF/build-receipt hashes, current report source and figure-input hashes, and the investor note's single Markdown source, generated LaTeX and two-page length. A separate visual-inspection record must identify the exact PDF hashes and every inspected page. That record describes research-assistant inspection, not independent human scientific review. The clean reproducer also rechecks all packaged file hashes after its commands, so source evidence is not silently overwritten during verification. These checks support artifact consistency; they do not establish scientific validity by themselves.
