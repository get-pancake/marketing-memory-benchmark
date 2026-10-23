# Development fixture data card

Version: controlled-events v0.1. Created 2026-10-21 for software validation.

## Origin and rights

All events, company identifiers, accounts, signals and catalog mechanisms are authored synthetic fixtures created in this research session. No customer records, production source, provider payloads or real company measurements are included. Generation is deterministic Python; no separate model was called to generate narratives. These fixtures are intended for redistribution under CC BY 4.0 with attribution to Pancake Research contributors, separately from the private working record.

## Contents and unit

Two fictional company worlds, each with six diagnostic checkpoints: initial context, weak feedback/proposed policy, an approved policy revision, a late-observed backdated correction, unavailable proof access and a stable control. The twelve cases are correlated development cases, not twelve independently sampled companies. Both worlds share a deliberately narrow template grammar; there is no held-out task-family split.

`dev/inputs.json` contains the catalog, complete event histories and public queries. `dev/labels.json` contains evaluator-only alternatives and condition labels. The runner applies time/access visibility before preparing the model prompt and never sends the labels. The source data files are public for software reproduction; being distributed with labels does not make them a hidden benchmark.

`dev/manifest.json` records exact hashes. `python3 -m prototype.fixtures` deterministically regenerates the files. Expected alternatives are authored by scenario rules and cross-checked against a separately evaluated action contract; this is not independent human annotation. No expert strategic-usefulness validation has occurred.

## Intended use and limits

Use for testing leakage, version/authority rules, typed support, failure preservation, model-client integration and dry-run feasibility. Do not use as evidence of superior generalization, commercial value, calibrated confidence, customer adoption or actual outreach effectiveness.

The fixtures omit natural-language extraction error, noisy identity resolution, heterogeneous domains, long histories, complex permissions and production-scale costs. The mock capability unit is an explicit test budget, not a dollar or latency forecast. These omissions must be addressed or scoped out in the eventual frozen protocol.
