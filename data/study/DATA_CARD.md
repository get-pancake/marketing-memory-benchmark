# Verified-event GTM Play fixtures

These original fictional records support a controlled comparison of evidence selection for research-Play proposals. They contain no customer data, provider exports or private Pancake source. Code and templates were authored with AI assistance in the research session. Python instantiation is deterministic; there were no separate narrative-generation model calls and no independent human annotations.

## Versions and splits

The retained `pilot-v1` through `pilot-v5` directories document development. Do not substitute an older fixture or scorer for its run. The current generator reproduces `pilot-v5` (two worlds, seed 2026102201), `runtime-smoke-v1` (one world, the same seed), and `main-v1` (12 worlds, seed 2026102202). Earlier snapshots preserve the code used for earlier runs. Manifest provenance wording in older development snapshots predates the explicit AI-assistance disclosure; “programmatically authored” does not mean independently human-authored.

Main data were generated before the first held-out inference. Main families are renewal, partner and compliance; development families are hiring and migration. Each world has eight queries, four answerable and four requiring evidence. There are 96 main queries, not 96 independent companies. All worlds share one generator and formal contract language. Family holdout tests combinations within that language, not external market generalization.

`inputs.json` contains full event histories, public catalogs and queries. `labels.json` contains acceptable-template sets and evaluator-only condition/family labels. The reader receives a permitted current subset of events, the query without the world ID, and the public catalog. Future events and hidden labels are never reader context. The files are distributed for audit; this is not a permanently hidden benchmark. Hashes in each manifest, the main freeze files and run ledgers identify the exact evaluated bytes.

## Semantics

An event has an immutable ID, world, entity, relation, value, authority, valid-from time, observed time, required scopes and explicit replacement links. Values and integer dates are fictional. Sources requiring multiple scopes require all of them. A replacement removes only a source in the same world/entity/relation/authority slot; unsuperseded conflicting values remain conflicts. This is a limited event model, not arbitrary bitemporal intervals.

Approved seller role and geography must match observed account role and geography. Family-specific slots supply a signal or state, an offering pain and proof. The catalog defines literal requirements, equality joins, objective and artificial step budgets. Two principal research alternatives share prerequisites; a qualification audit requires only common policy/account fit. A procurement alternative requires an executive-scoped fact. Each workflow step costs one artificial unit. Units are not money or commercial utility.

Conditions cover initial fit, weak feedback, approved targeting revision, account requalification, late/backdated correction, unavailable proof, changed objective and a conflicting approved policy. Noise levels cycle through 12/20/28/36 records; zero/one/two duplicate pairs are sampled independently of family. Names, identifiers, times, roles, geographies, template IDs and resource allowances vary. The main `design-summary.json` records the realized composition.

The listed conditions are in protocol order, not one uninterrupted chronological sequence. The restricted-proof query revisits the weak-feedback snapshot with reduced permissions; the changed-objective query revisits the requalified-account snapshot for a qualification audit. The late-correction query advances knowledge time while holding valid time at the requalified snapshot. The four reported transition pairs use the first five sequential conditions only.

## Ground truth and use

Construction rules specify sets of acceptable alternatives. Python and independently implemented SQLite contract evaluators must agree before writing a dataset. Both were authored within the same research process; agreement is a software check, not independent expert validation of GTM meaning. Negative decisions are scored without evaluating free-text explanations. Multiple eligible alternatives are accepted; no unique revenue-maximizing action is asserted.

Suitable uses are contract testing, controlled retrieval comparisons, provenance audits and research reproducibility. The fixtures do not establish strategic usefulness, campaign outcomes, learned feedback quality, robustness to natural-language extraction errors, full memory-product performance or production authorization security. All inputs are already structured and verified, and a deterministic policy evaluator can solve the formal eligibility problem directly.

License: CC BY 4.0 for the explicitly allowlisted data/output artifacts, with attribution to Pancake Research contributors (2026). Generator and scorer code use MIT. Third-party models, runtime and cited works retain their own licenses; see `release/THIRD_PARTY.md`.
