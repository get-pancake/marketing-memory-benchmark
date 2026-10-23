# Controlled-event Play recommendation harness

**Status:** runnable development infrastructure. No actual model pilot or main benchmark has run. This is not a claim of GTM specialization advantage. The critical literature review and main protocol remain open.

Python 3.12 or later is sufficient for the offline path; it uses only the standard library. Work from the repository/package root:

```sh
python3 -m prototype.fixtures
python3 -m unittest discover -s tests -v
python3 -m prototype.run --mode offline --output experiments/local-runs/my-offline-check
python3 -m prototype.summarize experiments/local-runs/my-offline-check
```

The output directory must be new. No attempt is overwritten. Start markers and completed/failed records are flushed to disk. Summaries retain the registered denominator even when a process is interrupted. This inexpensive path exercises a **deterministic policy reference and mock capability dry-run**, not LLM generation.

## Implemented boundary

Every retriever receives the same world, valid-time/observed-time cutoff and explicit scope filter. Visible supersession affects only records with the same subject/relation/authority. Proposals and non-responses cannot override approved strategy. Contradictory approved facts cannot be resolved by arbitrary record order. The method's prompt contains neither evaluator labels nor future records.

The catalog permits multiple acceptable research actions. Output is strict JSON, grounded in supplied event IDs, with a joint resource budget and a dry-run-only next step. The scorer verifies typed relations and support; it does not grade strategic usefulness, prose quality, demand, revenue or campaign outcomes.

The current ontology is intentionally small and hand specified. It is an engineering contract under test, not a validated model of GTM reasoning. Event relations and their canonical values are provided equally to every method. This controlled-event track does not evaluate extraction from raw company documents.

## Comparators

- `generic_bm25`: lexical reference over the visible verified record, with the common catalog and task.
- `prompt_specialized`: identical retrieval plus an explicit GTM checklist in the planner prompt.
- `typed_coverage`: prioritizes task-relevant public relation types, then uses the same ranking; shares the checklist with the prompt control.
- `full_context`: sends the complete visible record with the checklist. It reports failure if the record does not fit; it never silently truncates.

These are initial references. BM25 must not be described as a strong general-purpose memory system without further baseline work. Current typed coverage also changes ranking, so targeted ablations are required before attributing an effect to a single mechanism. Memory budgets are exact serialized UTF-8 bytes; they are **not token budgets**. Actual token usage and prompt hashes are saved when the endpoint supplies them.

## Actual model path

`python3 -m prototype.run --mode model --model-config /path/to/local-config.json --output experiments/local-runs/model-pilot` requires a real configured OpenAI-compatible chat endpoint. It never substitutes the deterministic policy reference. This command has not yet been validated with real model inference.

A loopback configuration has this shape (replace the model with the verified server model):

```json
{
  "base_url": "http://127.0.0.1:8080/v1",
  "model": "verified-local-model-id",
  "max_output_tokens": 600,
  "temperature": 0,
  "seed": 20261021,
  "timeout_seconds": 180
}
```

No local model weights are bundled. Verify their origin, exact revision/hash and license before loading. A small CPU model is suitable for a feasibility pilot, not automatically an adequate main-study backbone.

For a metered remote endpoint, HTTPS, a configured credential **name**, verified input/output prices, a user-authorized spending cap, an authorization reference and a price-source reference are required. Never place a credential value in JSON or Git. The accepted additional fields are `api_key_env`, `input_usd_per_million`, `output_usd_per_million`, `max_spend_usd`, `authorization_reference`, and `price_source`.

The runner reserves conservative costs before each call and does not retry. Reservations are not billing receipts; provider-specific token overhead, caching/reasoning prices and external budget enforcement still need verification. Actual usage and usage-based estimated API cost are distinguished from billed cost (unknown). CPU/cloud infrastructure cost is not assigned an invented dollar price. A model access/spending decision remains necessary before metered calls.

## Completion gates

The CLI currently refuses non-development splits. Before a main study: complete the nearest-work review, choose a narrow contribution, independently check task validity, implement a capable generic/hybrid baseline, define the primary outcome and essential ablations, use a development pilot to assess variance/resources, then freeze the protocol, implementation, model settings and world/family split. Removing this gate requires a documented protocol amendment. Do not relabel these development fixtures as held-out data.
