# Contributing

We welcome attempts to reproduce, challenge or improve these results. Useful contributions include stronger generic-memory baselines, independent company histories, raw-document ingestion, budget sensitivity and practitioner evaluation.

## Preserve the evidence

- Keep the original `data/`, `experiments/` and frozen source snapshots intact. Put new datasets, methods and runs in explicitly versioned paths.
- Compare methods on the same cases and reader settings. Disclose any extra input, tuning, compute or model calls.
- Retain all attempted calls, including failures. Use company-level paired analysis rather than treating repeated queries as independent companies.
- Separate deterministic checks, cached-response analysis, fresh model inference and human assessment. Generated judgments are not human validation.
- Include licenses and provenance for new data or code. Do not contribute customer records, secrets or materials without redistribution rights.

## Validate a change

Run the inexpensive checks in the root README. For changes to scoring or analysis, explain the intended behavior and add focused tests when warranted. Report whether saved-output reproduction passed and whether any fresh inference was performed. Public CI performs offline checks only; it must not require API keys.

Provide the command, environment, affected case IDs and output when reporting an issue. Do not upload credentials or unrelated private logs. Changed methods should receive a new experiment version rather than silently rewriting the published benchmark.

Original code contributions use MIT; original data and documentation follow the CC BY 4.0 scope in `LICENSE-DATA`. Third-party material retains its own license and attribution.
