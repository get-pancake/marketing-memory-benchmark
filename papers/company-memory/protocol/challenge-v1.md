# Prospective challenge protocol, v1

Recorded prospectively before challenge pilot/model execution; no external preregistration is claimed. UTC date: 2026-10-23. Prior v3 studies and their analysis are unchanged; this new benchmark is motivated by their ceiling effects and the user's requested Opus replacement.

## Task and provenance

Original, programmatically authored fictional companies; no private/customer text. Each world has three stress levels: 4/6/8 candidate accounts, increasing corporate distractors and temporal/conflict cases, and evidence budgets of 16,384/12,288/8,192 UTF-8 bytes. The compound levels are not a factorial causal estimate of individual difficulty mechanisms. Each query asks for at most three distinct-account actions from a shared catalog under a shared resource budget. Eligibility follows current approved policy, consent, an initiative → need → offering → proof chain, a signal and action-specific operational/legal prerequisites. The score maximizes explicit synthetic policy priority points, never predicted commercial return.

Every memory receives the same visible records. A shared, tested visibility/current-view layer handles valid time, observation time, access, explicit supersession and approval. Conflicting current values are not resolved by popularity or retrieval score. This is a controlled representation/retrieval experiment, not end-to-end raw-document ingestion. Labels, optimal plans, future and unauthorized records are excluded from input packets.

## Treatments and competence

- No company context: same query/catalog/reader, no company records; information reference.
- Company context: pinned native GBrain hybrid ranking plus domain-neutral entity/link closure.
- GTM context: same ranking with closure restricted to catalog-required relations; no truth-value/utility scoring in retrieval.
- Markdown control: local BM25/dense reciprocal-rank fusion plus the same domain-neutral entity closure; original structured wiki pattern, not an official Karpathy implementation.
- GBrain search: actual pinned native hybrid ranking alone.
- Full current context: unbounded evidence reference, disclosed greater input cost.

GBrain and Markdown use the same real OpenAI embeddings. Catalog, instructions, output schema, decoding settings and byte budget are equal within reader except the explicitly unbounded full-context reference. The company and GTM contrast changes only retrieval/packing. Source IDs are citation constraints, not answer labels. No oracle chooses which evidence to include. API failures/truncations count as failed responses, with no automatic replacement or answer repair.

Actual readers: gpt-6.1-sol, reasoning medium; claude-opus-5-5, adaptive thinking, high effort, subject to real settings validation. Cross-provider effort is not asserted compute-equivalent. Within-provider treatment contrasts are primary.

## Outcomes and analysis

Primary: grounded feasible policy value divided by full-information optimum, on cases with nonzero optimum. A plan violating any global constraint, eligibility requirement or required citation receives zero; report its valid-action components separately. Secondary: exact optimum, actionable coverage, unsafe/unsupported plan rate, inappropriate abstention, context-recoverable normalized value, latency and estimated API cost. Zero-optimum cases contribute to a separately reported safety denominator, never to the primary value score. Full-information reference is a rules/optimization diagnostic, not a memory or LLM baseline.

Pair each treatment on the same cases; aggregate equally across difficulty levels within company and resample company worlds, stratified by the three scenario families. Use 10,000 bootstrap samples and 95% intervals for mean paired differences. Primary confirmatory contrasts: GTM minus Company within each of two readers; Holm adjustment for two paired random-sign tests. Other comparisons, difficulty slices, retrieval budget sweeps and qualitative error analysis are descriptive. Bootstrap intervals are conditional on the synthetic generator and cannot establish population effects for real firms. Report all dimensions and absolute denominators. For zero-variance/tied contrasts do not claim formal equivalence.

## Pilot, sample and freeze

Development pilot: 12 worlds, all three levels, all six arms and both readers. Inspect mechanics, competence, format failures and accounting. Amend only before main freeze, retaining old pilot artifacts. Sample size: let s be the larger pilot standard deviation of the company-level primary paired difference across the two readers. Set n = ceiling((1.96*s/0.05)^2), round up to a multiple of three, bound to [120,192]. This is an approximate precision planning rule, not an outcome-driven power guarantee; report cap if reached. Main uses a different seed and fresh worlds; generator/task families remain known. Freeze code, data, prompts, model settings, analysis and exclusions before issuing main calls. Do not stop early on significance or enlarge after viewing main outcomes.

Ground-truth audit: independent SQLite eligibility query and separate enumeration solver on pilot; meaningful invariance tests for temporal/access boundary, conflict, proposal/non-response, ties, budget/duplicate-account constraints and citation sufficiency. This is an independent implementation check by the same research agent, not human/independent-author validation.

## Release

Retain raw requests/responses, failures, model IDs, usage, code/data hashes, selected evidence and ranked lists. Public package includes original code/data and permitted upstream attribution, not credentials, private planning, full copied web pages or private product sources. Saved-output reproduction and fresh inference are separate commands. Public publication and venue submission are not implied by a tested private release candidate.
