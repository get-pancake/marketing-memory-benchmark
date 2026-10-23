# Context quality to action quality — integrated prospective protocol

22 October 2026. Registered in the private research repository before the new reader pilot. One report supersedes the earlier two-paper proposal. Prior v1/v2 results remain historical/exploratory; this study uses new worlds and real provider calls. No positive result is required.

## Questions and intervention

RQ1: At a common evidence budget, does action-relevant coverage preserve more complete current evidence than strong general memory? RQ2: Does changing that context improve grounded action decisions within each same reader? RQ3: Can a generic file-memory or the same selection layer on GBrain close the gap?

The intervention is the selected evidence packet. Every method shares the same approved/observed/proposed records, common valid-time/observation-time/access boundary, public action catalog and competent domain-aware reader prompt. The planner is fixed within a model. No-label, no-future and no-cross-scope boundaries apply before every selector. No retrieval metric is inferred from the reader's answer.

## Comparisons

| Arm | Executed mechanism | Interpretation |
|---|---|---|
| None | Common task/catalog; zero company evidence | Information-availability baseline; appropriate abstention is not a model defect |
| Generic | BM25 + text-embedding-3-small, RRF k=60 | Strong domain-prompted general fact retrieval |
| Markdown | Lossless current-state entity Markdown files; same generic retrieval with domain-neutral field/authority diversity | Reproducible structured-file component inspired by LLM-wiki practice; not Karpathy's implementation or an LLM compilation evaluation |
| GBrain | Pinned native PGLite/balanced hybrid search with the same real embedding vectors | Actual search component, not hosted product or full native ingestion |
| Specialized | Same generic ranking plus coverage of public action prerequisites | Catalog-conditioned selection; no answer-value or label filtering |
| GBrain + specialization | Same coverage operation over native GBrain ranking | Same-backend control; specialization may be composable with general memory |
| Full context | All permitted current records | Direct reader reference; larger actual cost, not a matched-budget arm |

GBrain pin: 531b3b1ab66c88f192abb51338028c44b80fbf21. Domain prompt/glossary and all catalog requirements are common to every arm, so Generic is also the strong prompt-specialized control. We do not attribute an instructions change to memory. Common canonical evidence encoding removes rendering as a confound; Markdown's stored representation is preserved for inspection. Query/indexing code and maintenance boundary are disclosed.

Primary evidence allowance is **2048 UTF-8 bytes** of the common canonical evidence array, excluding the common instructions/catalog. This is a reproducible serialization budget, not a claim of exact provider token matching. Actual input/output/cache/reasoning token counts are reported separately. Whole records are packed greedily; no record text is truncated. Retrieval-only sweeps use1024,2048,4096,8192bytes. None and Full are explicit unequal-information/resource references. Every provider receives byte-identical contexts for the same arm/case.

## Data and scoring

Use original fictional company worlds from the previously frozen, independently cross-implemented Python/SQL contract generator, with new disjoint world seeds. Pilot:4 worlds,32cases, hiring/migration families, seed2026102231. Main worlds use renewal/partner/compliance families and a new prespecified seed. These are repeated templated worlds, not sampled real companies or independently authored business decisions. Existing externally authored MIT company documents support a separate exploratory qualitative track; they do not increase the independent-company count.

Eight conditions/world include approved policy changes, account requalification, evidence correction, access restrictions, weak feedback, objective changes and unresolved conflict. Four cases are answerable and four require withholding. Multiple acceptable actions are allowed. Labels remain outside reader requests. A full-context deterministic SQL reference establishes what the task checks; perfect rule satisfaction is not optimal commercial strategy.

Primary context outcome: complete acceptable current support on answerable cases. Supporting context outcomes: required-value-group coverage, source precision and false apparent eligibility caused by hiding a conflicting value. Primary reader outcome: grounded correct decision across all attempted cases (supported valid recommendation on positives; correct withholding on negatives). Separately report positive recommendation coverage, unsupported recommendations, inappropriate abstention, schema/transport failures and mock dry-run feasibility. A no-context reader is expected to withhold: its lower coverage quantifies missing information, not specialization. Main specialization contrasts compare methods that access exactly the same source bank.

Score every raw response before any common validator. The optional deterministic validator only checks supplied evidence and never imports hidden labels or repairs citations; its separate outcomes must not be described as an LLM improvement. Explanations support a qualitative case review but are not assigned invented human usefulness scores. No model judge determines the primary outcome.

## Readers, costs and failures

GPT-6.1 Sol (`gpt-6.1-sol`, reasoning low) and Claude Sonnet5.5 (`claude-sonnet-5-5`, provider default; temperature is unsupported). Provider model lists and actual availability responses are archived. Fix within-model settings across every context arm. Max2048outputtokens; no tools, external web, or conversation history during a recommendation. Output includes an evidence-binding table, decision, selected action, missing information and brief explanation.

Standard pricing checked against official pages22October: both readers $2/M uncached input and $10/M output; cached reads $0.10/M; standard cache writes $2.50/M (OpenAI30min, Anthropic5min). OpenAI12hour writes cost $5/M; Anthropic extended-cache pricing is unverified and no extended cache is requested. A $5/M input reservation is a conservative operational bound, not a claimed Anthropic tariff. text-embedding-3-small $0.02/M,1024dimensions. No explicit cache creation is requested. Distinct provider cache accounting is implemented and actual usage preserved. Prices give estimates, not verified invoices. Preflight reserves an intentionally conservative byte-plus-framing input upper bound and maximum output; keeps reservations for failed/interrupted requests. Researcher-selected numerical execution guards are disclosed as operational caps, not amounts specified by the user. User explicitly authorized API benchmark execution. No keys appear in artifacts.

No automatic retries, silent fallback or response replacement. Retain API errors and schema failures in the denominator. Stop on authentication/rate denial or unexpected usage. One provider request per case/arm; deterministic shuffled order, bounded concurrency and no selective repeated sampling. A resumed issued-but-unfinished request becomes interrupted and is never reissued. All requests, responses, usage, elapsed time, code/data hashes and unsuccessful attempts are saved.

## Pilot, freeze and analysis

After pilot, correct implementation defects and assess competent baselines. Determine main company count using the maximum within-model paired world-mean SD for Specialized minus Generic, target normal-approximation half-width0.075: ceil((1.96 SD/0.075)^2), rounded up to a multiple of3, minimum24, maximum60. This is a resource-aware precision rule; four pilot worlds give uncertain variance, and the60-world ceiling may miss the target. No outcome-based stopping or sample-size changes after the main freeze. Freeze seed, count, code, prompts, model config, input hashes and analysis code before main reader outcomes.

Report per-model paired percentage-point contrasts and95% company-world bootstrap intervals, stratified by held-out family; repeated cases are not independent units. Primary contrast is Specialized−Generic within each reader; a joint claim requires both to support improvement, with Holm-adjusted exact paired sign tests over world differences. All other pairwise comparisons and budget sweeps are secondary/descriptive. Report every arm even if it invalidates a preferred story. Clustering does not remove shared-generator or synthetic-data limitations. Descriptive success conditional on complete evidence is not causal mediation.

Main figures: experimental matrix; context support versus budget; within-model quality/coverage; paired improvement intervals; error/abstention composition; quality versus actual token/cost consumption. Include representative successes, baseline wins and failures selected by a stated rule. Keep prior experiments clearly separated and avoid pooling their model responses with the new study.

## Publication claim boundary

This controlled study can test evidence selection and grounded action eligibility with a fixed planner. It cannot prove universally superior company memory, strategic optimality, raw-document extraction, revenue, customer retention or network effects. A public MIT/CC-BY companion can reproduce saved analyses and enable fresh provider runs with independently supplied keys. Native Goal activation is unavailable in this runtime; objective/state files support manual resumption.


## Development amendment A — common native structured output (23October00:08UTC)

The first reader pilot was stopped for an interface defect after132issued/124valid responses: eight Anthropic outputs had malformed JSON. All132attempts and316unissued plans remain recorded, estimated usage cost$1.0521. No favorable replacement is inserted into that run. Both providers now receive the same native JSON schema built solely from public catalog slots and supplied source aliases, including null/missing values and every catalog action. The schema constrains serialization, not answer eligibility. First Anthropic schema syntax (nullable type-list with enum) was rejected; common anyOf syntax passed actual provider checks. A separate complete development pilot is required before sizing/freezing the main study. Conservative input reservations now include the schema bytes. Observed quotas allow bounded16-request concurrency; this changes pilot throughput, not per-arm reasoning resources. Exact rate headers and all schema-integration attempts are retained. OpenAI default30minute cache-write accounting was verified against its official guide; explicit12hour counts, if returned, are costed separately. No extended Anthropic cache is requested.
