# Frozen main evaluation — 22 October 2026

This protocol is finalized before the first held-out model request. The private working repository is not a public release. Exact freeze files, source snapshots and dataset hashes accompany the runs.

## Scope and decision to advance

Test catalog-conditioned evidence coverage over common verified events, conditional on one fixed reader and explicit Play contracts. This is a controlled fictional study, not raw-document ingestion, learned strategy, independent expert assessment, production validation or commercial outcomes. All methods already receive typed facts and provenance. The algorithm is reusable outside GTM; no uniquely GTM algorithm or new memory architecture is claimed.

Development progressed through retained 4B, 9B and MoE competence failures, then a common support-table interface and clarified alternative-specific prerequisites. The completed 48-call Stage B had eight cases per method: typed and full context each 5/8 correct, prompt hybrid 3/8, generic hybrid 3/8, facet hybrid 4/8 and history ablation 5/8. Full context retrieved complete support on every positive case but produced a supported recommendation on only 2/4. This shows that reader errors remain material; full-context availability is not an oracle answer. The study proceeds to quantify that limit rather than tuning the two worlds until perfect. No main outcomes informed these choices.

The Stage B source-binding diagnostic exposed a reporting taxonomy issue: repeated source bindings became duplicate flat citations and were counted as shape errors. The final materializer projects a citation set while preserving every original row binding for strict semantic checking. All 48 pilot decisions were rechecked: primary outcomes are unchanged; six diagnostic records change category. Original scores are preserved alongside the audit. The prompt, model and retrieval behavior do not change for this correction.

## Data, sample size and estimand

Main dataset: `data/study/main-v1`, seed 2026102202, generated on 22 October 2026 after development. Twelve company worlds, four per held-out family (renewal, partner, compliance), with eight cases per world: initial, weak feedback, policy revision, account requalification, late/backdated correction, restricted proof, objective change and policy conflict. Forty-eight positive and 48 negative queries. The two pilot families (hiring/migration) and their worlds are excluded.

World names, roles, geographies, date gaps, template IDs, resource limits and duplicate pairs vary. Noise levels 12/20/28/36 cycle across worlds; duplicate pairs are drawn independently of family. Programmatic construction labels agree with separate Python and SQL evaluators. This is not independently authored human ground truth. Future events, labels and condition names are excluded from reader messages; requester permissions and both time axes are enforced before retrieval.

The primary estimand is the mean paired world difference in supported-decision accuracy, catalog coverage minus prompt hybrid, at 1,024 input tokens. Stage B world differences were 0.25 and 0.25 (SD zero), so the prospectively recorded planning floor of 0.20 applies. The rule `2.202 * 0.20 / sqrt(N) <= 0.15`, with N >= 12 and balanced families, selects N=12. Its planning half-width is approximately 0.127; this is a heuristic precision estimate, not a promised achieved interval or evidence of an effect. World count is not inflated by queries, methods or seeds.

## Frozen comparisons and computation

Primary block: all six methods at a 1,024-token total-input cap, 12 x 8 x 6 = **576 planned logical attempts**. Methods: `generic_hybrid`, `prompt_hybrid`, `facet_hybrid`, `typed`, `full_context`, `typed_history`. Full context has a 15,000-token safety cap and is a separately priced reference, not a matched-budget claim. Ordering seed 20261022.

Budget sensitivity: `prompt_hybrid` and `typed` at 1,536 input tokens, on the same 96 queries: **192 planned logical attempts**. Ordering seed 20261023. This secondary block is exploratory; it tests whether retrieval advantages depend on scarce context. No additional tuning or sample selection occurs between blocks. Run the primary block first, then sensitivity, with the same runtime. Do not interpret observational timing differences across blocks as a controlled hardware speedup.

Common reader: pinned Qwen3-30B-A3B-Instruct-2507 Q4_K_M, non-thinking checkpoint, temperature 0, seed 20261022, maximum 280 output tokens, one planned reader decision per attempt and no answer repair. Embedding: pinned Qwen3-Embedding-0.6B Q8_0, last/EOS pooling, 1,024 dimensions and normalization. Shared BM25/RRF and public-catalog query expansion. Runtime hashes, exact request JSON, returned model IDs and defaults are recorded. Four CPU threads, 32 GiB memory limit, no GPU or paid endpoint. Secondary generation requires the same resources; the observed pilot suggests several hours for the full study.

Use a new empty embedding cache in the primary output directory; sensitivity may reuse that common index, retaining origin receipts. No main generation response is imported from development.

## Identical-request reuse and failures

Stage B issued every call independently: seven groups of repeated, identical model inputs (15 calls in total) all returned identical raw outputs. For the main blocks, enable one-response-per-identical-serialized-request reuse **within each run only**. The key includes the complete request body, preserving schema property order, model, messages, decoding seed/settings and output cap. All returned responses are reusable, including malformed, truncated or incorrect ones; correctness never controls caching. The first response is an actual local model execution. Every reused attempt retains its exact origin, raw output, usage and response ID. There is no cross-run generation cache and no synthetic or mocked answer fallback.

Report 768 planned logical attempts separately from the actual number of physical generation requests. Primary scoring includes every logical attempt. For method-level resource comparisons, charge the origin call's observed tokens and generation time to identical requests; report actual physical totals separately. Reuse asserts a conditional deterministic response for identical inputs and does not measure stochastic repeatability beyond the pilot audit. This design does not make repeated inputs independent samples.

An exclusive run lock prevents duplicate execution. On explicit `--resume`, already issued attempts with no saved terminal record are closed as interrupted failures, preserving unknown usage; completed/failed calls are never retried. Only unstarted work resumes. A torn last write is archived before repair. Transport failure stops the run for repair rather than producing a cascade of artificial case failures. Preserve all attempts and any necessary infrastructure amendments.

## Outcomes and analysis

Primary: correct applicable recommendation with complete relevant current support and correct per-slot bindings, or correct withholding when no catalog alternative is supported. A failed/missing attempt is zero. Withholding every time scores 0.5. Multiple acceptable alternatives are allowed. The deterministic SQL full-record reference is an exact policy diagnostic, not an end-to-end memory competitor.

Supporting dimensions: template choice without support correctness; positive-case supported coverage; complete witness availability in retrieved context; inappropriate withholding; recommendations on negative cases; schema versus semantic binding failures; executed mock dry-run completion; transitions before/after changes; input/output tokens, retrieval/embedding/generation time and physical versus charged computation. Free-text missing-evidence explanations and strategic usefulness are not scored. Mock resource units count fixed tool steps, not dollars or commercial utility.

Compute paired world means and 95% percentile bootstrap intervals from 10,000 draws, seed 7201, resampling worlds within each fixed family. This targets variation in the fictional generator conditional on these families/model. It does not estimate commercial-population uncertainty or generalization to an arbitrary new task family. Report all world values and dimensions; degenerate intervals are not guarantees. No significance shopping, unplanned superiority claim, or equivalence conclusion from nonsignificance. Other method contrasts and the budget sensitivity are explanatory/exploratory, with no family-wise significance claim.

Analyze after both blocks, retaining errors. Generate figures and tables from saved summaries. Source/data/configuration hashes are in `experiments/freeze-1024.json` and `experiments/freeze-1536.json`; run source snapshots allow exact audit. Any subsequent code or analysis correction must be recorded, with original artifacts preserved. Paper statements must distinguish deterministic checks, real generation, cached real responses, mock execution and unmeasured real-world outcomes.
