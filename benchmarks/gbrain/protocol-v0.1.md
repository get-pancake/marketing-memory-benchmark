# GBrain integration diagnostic — declared before first adapter execution

22 October 2026. This is a post-v1 component diagnostic on already observed
research fixtures, not a newly hidden market benchmark.

- Pin actual GBrain source at `531b3b1ab66c88f192abb51338028c44b80fbf21`.
- First smoke on one development case, then pilot all 16 development cases if
  integration is sound. Resolve engineering errors on development only.
- Compare the actual balanced upstream hybrid path and the existing generic,
  facet and required-slot coverage ranking on the same prefiltered event view,
  same Qwen vectors and exact common prompt-token budget. Full context remains
  separately costed. Do not configure domain-specific constraints only for us.
- Disable paid expansion/reranking and do not describe this as the vendor's
  maximum-quality deployment. These options are unavailable resources, not
  algorithm ablations demonstrating their lack of value.
- No constructed graph: the v1 atomic records lack independently extracted
  document links. Do not infer a graph ranking from this flat-source task.
- GBrain returns a full ranked pool; the shared greedy packet builder applies
  the original total 1,024-token budget. Record rank pool size, exact input,
  timings, vector-arm use, selected IDs, failures and token count. If GBrain's
  native return policy limits the pool, disclose rather than silently invent
  remaining ranks.
- Query text and embedding are exactly the existing `query_text` function and
  real cached embeddings. Reusing vectors is allowed, with their origin costs
  retained. Ranking is executed anew. There is no model generation in this
  diagnostic.
- Outcomes: complete positive witness availability; current relevant-value
  coverage; stale/ineligible sources; false apparent eligibility; search/index
  time. No recommendation accuracy, hosted price or revenue is inferred.
- Re-running all 96 v1 cases would be exploratory because these data and their
  results have already been inspected. Freeze a new independent split for any
  confirmatory market claim. Preserve failed integration attempts separately.

## Development amendments (before exploratory 96-case extension)

The first 16-case run retained four cache-miss failures and 12 actual completed
GBrain searches. Three actual local embedding requests completed the shared
cache; the second development run completed all 16 searches. No provider
generation was used. The first smoke's reranker fallback was replaced by the
explicit upstream `search.reranker.enabled=false` setting; the second run has
no reported degraded stages.

Development showed weak coverage for the plain upstream ranking on the atomic
catalog fixtures. Before extending to the 96 already-known v1 cases, add a
**same-backend GBrain + catalog-coverage control**: apply the identical public
prerequisite/diversity module to GBrain's saved full ranked pool. This shares
both the backend and retrieval output and needs no new upstream/model request.
If this control closes the gap, the result favors composing a task-specific
selection layer with general memory, not replacing that memory or claiming a
unique vertical storage architecture. This is development-driven analysis;
the 96-case extension remains exploratory, not a new preregistered main study.

The 1,024-token cap deliberately stresses selection and is not a representative
default company-memory allowance. Before analyzing the exploratory extension,
also declare 1,536- and 4,096-token packet-building sensitivities for every arm.
These reuse saved actual GBrain rankings and real shared embeddings; they add
no GBrain/native generation calls. Report the full sweep, including ties or
reversals, rather than claiming a universal advantage from a constrained budget.
# Offline reproduction correction — 22 October 2026

The first clean-package reproduction passed the 1,024-token analysis but failed
at 1,536 tokens: a local retrieval-receipt variable shadowed the token-receipt
closure. The executed native rankings and live-tokenizer analyses were unaffected.
The fix names the tokenizer receipt separately. A regression check replays a real
positive case through all six controls while prohibiting network requests.
Initial tokenizer analyses are preserved as `analysis/gbrain/pre-offline-fix-*`;
the corrected canonical `reproducible-*` outputs must retain identical selected
source rows and tokenizer counts, with only the analysis-script hash changing in
their summary. This is a reproduction-code correction, not a new experiment or
an amendment to outcome selection. The failed clean-reproduction receipt is kept.

