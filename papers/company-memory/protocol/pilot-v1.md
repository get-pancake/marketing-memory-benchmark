# Verified-event pilot protocol

Recorded 22 October 2026, before model execution of `study/`. Main evaluation is not yet frozen.

## Question and scope

Does catalog-conditioned GTM prerequisite coverage improve supported Play choices beyond generic lexical+dense retrieval, a GTM checklist, and domain-neutral diversity? This is a controlled verified-event study. It does not estimate extraction accuracy, unconstrained strategy quality, customer utility, campaign outcomes or superiority to deployed Hindsight/Graphiti systems. The literature/reuse decision is `literature/GAP_AND_REUSE.md`.

The domain-specialized prototype prioritizes catalog-required entity/relation/authority groups. The selection algorithm itself is reusable outside GTM; any finding must not imply a uniquely GTM algorithm or a proprietary ontology moat. All methods already receive the same typed facts. This isolates task-aware retrieval, not the entire effect of introducing domain semantics into an unstructured memory.

## Task

The planner selects at most one of four shared catalog templates, citing every required current source, or requests evidence. Two alternatives can be acceptable. Seller role/geography policy must match account observations; additional prerequisites vary by task family. A qualified proposal is materialized into a Play specification with objective, account, policy versions, sources, mechanism hypothesis and computed units, then executed against three deterministic mock research capabilities. No contact or production change occurs.

Eight conditions per fictional world: initial eligibility, weak feedback, approved policy revision, account requalification, late/backdated evidence correction, permission-restricted evidence, objective change and a conflicting approved policy. Four are answerable and four require withholding. Query labels, condition names and future/unpermitted facts remain outside planner inputs. Valid and observed times are distinct; supersession is explicit. Catalog constraints are public task definitions, not secret answer keys.

Pilot families are hiring/migration; planned held-out families are renewal/partner/compliance. Structural unit checks exercise all contracts, but no model outputs from held-out families will be used to tune methods. The held-out world seeds and run plan are generated only at the main freeze. All worlds share a programmatic generator and author; no independent human assessment is claimed. Construction labels are checked by separately implemented Python and SQLite evaluators.

## Methods and information budgets

All methods share entity scoping, permissions, time cutoffs, catalog, Qwen3-4B-Instruct-2507 Q4_K_M and one planner call. Temperature 0, seed 20261022, output cap 280 tokens, no automatic retries. Each attempt is retained, including malformed output and failures.

1. `generic_hybrid`: BM25 + Qwen3-Embedding-0.6B Q8_0, reciprocal-rank fusion (60), base task instructions.
2. `prompt_hybrid`: identical retrieval ranking plus the GTM checklist. The common total prompt cap means the shorter generic prompt may admit more evidence; report actual counts.
3. `facet_hybrid`: same hybrid ranking and checklist, round-robin distinct entity/relation/authority groups, without consulting required slots.
4. `typed`: same ranking/checklist, prioritizing public catalog prerequisite groups before the same diversity mechanism.
5. `full_context`: all eligible facts, same checklist. A separately priced reference; not claimed to share the bounded input allowance.
6. `typed_history`: typed retrieval without deterministic supersession removal, retaining replacement links and times for the shared planner to resolve. Future/time/access filters remain active.

Bounded methods use at most **900 actual input tokens**, including instructions, catalog, query and evidence. Counts use the same llama.cpp chat template and tokenizer as generation and are checked against actual usage. Full context must fit 15,000 input tokens or fail explicitly. It is never silently truncated. These are experimental settings, not a fabricated persistent-Goal token budget. No metered API access is used.

The shared hybrid query expansion includes all relevant catalog prerequisite names for every method. The generic controls therefore are not deprived of the domain vocabulary. Typed retrieval cannot read gold labels or choose fact values from answers. Fixed resource units equal mock tool calls, one per step.

## Pilot stages and advancement

Stage A: confirm the compact prompt can produce fully cited valid proposals on the two development worlds, using full context and typed retrieval. Four actual calls are planned. The earlier UUID-heavy calibration is retained separately at `experiments/development/2026-10-22-inference-calibration/`; it is a failed/limited development comparison, not a main result.

Stage B: compare all six methods on initial, policy-revision, restricted-evidence and objective-change cases in both pilot worlds (48 calls), unless Stage A reveals a design defect requiring a recorded amendment first. Examine every failure, baseline competence, selected evidence, prompt lengths and actual latency. Do not select hyperparameters from main results. If the small model cannot follow the contract even with full evidence, revise the prompt on development data or explicitly narrow the claim rather than treating a broken baseline as evidence for specialization.

Choose the main number of worlds from the observed paired world variation and a practical CI-width target, with a conservative variance floor because two pilot worlds are not a stable variance estimate. Balance held-out families and document CPU-time requirements before the main freeze. Counts in this pilot protocol are planned executions, not results.

## Outcomes and analysis

Primary: correct supported decision, with every planned case in the denominator. A recommendation must be applicable and completely cited; withholding is correct only when no catalog alternative is supported by the complete permitted current record. Every world has equal positive/negative weight, so always withholding scores one half, not perfect performance.

Report separately: applicable choice ignoring citation completeness; supported recommendation coverage on positives; inappropriate withholding; recommendations on negative cases; schema failure; full-support availability; mock dry-run success; policy/update and stable-transition behavior. Uncertainty resamples paired **worlds**, not individual repeated questions or decoding seeds. Paired comparisons and world-level distributions matter more than a single aggregate. The primary main contrast will be typed versus the strong prompt-specialized generic hybrid; the generic diversity comparison diagnoses the mechanism. Do not claim equivalence from a nonsignificant difference.

Record generation tokens/time, retrieval time, unique embedding ingestion/query receipts and cache origins. A shared index can be reused, but later methods must not be credited with zero ingestion cost because they hit a cache warmed by another method. Local API spend is zero; electricity, hardware rental and dollar total cost are unknown. Main method ordering is seeded and randomized. Run generation and embedding requests serially within a benchmark. Other compute during the early calibration is disclosed; those timings are not a controlled latency result.

## Reproducibility and integrity

`study/run.py` gates test data on a freeze file matching code hashes, dataset hashes, model configuration, method list, token cap and ordering seed. Every planned attempt has durable start and model-call records, raw messages/output, selected IDs and terminal status. No failed attempt is removed from scoring. The main freeze and any amendments must be committed before dependent execution. Saved outputs can reproduce analysis without implying a fresh model rerun.
