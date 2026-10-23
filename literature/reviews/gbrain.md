# GBrain — implementation and evaluation audit

Inspected 22 October 2026 UTC as a general-purpose memory comparator. Owning source: https://github.com/garrytan/gbrain at `531b3b1ab66c88f192abb51338028c44b80fbf21`, version 0.60.380.0, MIT. Evaluation repository: https://github.com/garrytan/gbrain-evals at `6999ebc9da0ac784ac05995b586d22293544e924`, MIT with dataset-specific attributions. Dated source requests and hashes are in `literature/retrievals.jsonl`; large upstream code is an ignored cache, never copied wholesale into our public companion.

## What the system already solves

The README describes portable shared memory, provenance, corrections/withdrawal, source/operation permissions, keyword and semantic search, optional typed graph retrieval, synthesis and background maintenance. These are prior capabilities, not missing features we may pretend to introduce. Company memory need not be unstructured or lack domain semantics.

Inspected `docs/architecture/RETRIEVAL.md`, the company-brain tutorial, engine/page-projection APIs, `src/core/search/hybrid.ts`, mode configuration, embedding gateway and public tests. The actual hybrid path combines lexical/vector candidates and post-fusion controls; balanced mode exposes graph-related features and optional paid reranking. Atomic verified events without an extracted relation graph exercise only part of that system. A local component result is not the hosted product, its best paid configuration or a scale/authorization benchmark.

## Upstream empirical evidence and limits

The September 9 retrieval-refresh report explicitly separates complete-evidence retrieval from model answering, gives paired gains/losses and notes missing raw judge evidence. Its later correction says answer-session identifiers leaked evidence membership into a prior answering result; that number must not be reused as a clean comparator. The October 4 follow-up reportedly confirms retrieval with opaque IDs. These are upstream reports, not experiments we reproduced. Do not compare their scores directly to our small contract fixtures.

`eval/CREDITS.md` identifies project-authored adapters and AI-authored question placeholders, with no human external query contributors recorded in that section. This is not independent human validation. The inspected source also reports non-improving expansion configurations; it is not appropriate to select only its successful headline numbers.

`messy-company-v1` provides a useful external development corpus: one fictional seller, account-cluster splits, messy prose, policy/ownership changes and deterministic labels. The documentation describes model-authored pages and cross-model checks. The development subset is hash-verified locally; the held-out pages/labels have not been downloaded. Its account clusters are not independent real seller companies. The root MIT license and upstream attribution remain attached. Corpus adoption reduces same-project authorship, not every source of synthetic-data bias.

## Executed reuse and boundaries

`benchmarks/gbrain/search.ts` invokes the actual pinned PGLite engine, revision-bound page projection and hybrid search. It passes real shared Qwen embeddings through the upstream injectable query-vector seam and records whether the vector arm ran. No fake ranking or model output is substituted. Provider reranking is explicitly off, and source graphs/ingestion/synthesis are outside this diagnostic.

The first standalone smoke succeeded. A subsequent 16-case development attempt retained four embedding-cache failures; three actual local embedding calls completed the cache, and all 16 cases ran on the next attempt. The plain ranking had poor prerequisite-set coverage on these deliberately narrow atomic fixtures. A same-backend control applies our identical public prerequisite-selection module to GBrain's returned pool. This prevents attributing a composable task-selection benefit to a unique database or assuming general memory must be replaced.

The initially attempted 96-case extension pointed at the development cache and failed all cases before a GBrain query. That failed ledger is preserved. A corrected run uses the exact original main-study embedding cache, without changing vectors. The extension is explicitly exploratory on already observed v1 data, not a new confirmatory market study. See exact manifests and outputs in `experiments/gbrain/` and `analysis/gbrain/`.

## Reuse decision

Keep GBrain as an actual, pinned comparator and possible substrate for domain-specific retrieval. Keep the same-backend specialization control. Adopt external raw-document cases for the prospective memory study after checking label sufficiency and budget/permission boundaries. Do not claim graph superiority, independent expert validation, a whole-product win or a novel marketing-memory architecture from this integration diagnostic.
