# Contribution decision, 22 October 2026

This decision precedes the main study. It follows critical review of RAMP, IFCMemoryBench, MARS and the closest memory/retrieval/action papers summarized in `reviews/`. The search has limits and does not establish an exhaustive novelty claim.

## What survives the review

The appropriate contribution is a **controlled empirical technical report and an executable GTM Play fixture suite**, not a new general memory architecture. Prior work already combines marketing memory with planning (RAMP), domain memory with live tools (IFCMemoryBench), evolving beliefs with recommendation (MARS), temporal evidence with proof-supported decisions (EviGraph), and bounded complementary retrieval with a shared reader (MemCompile). MemDerive already evaluates derived-state correctness, support and update behavior. Merely renaming those mechanisms would add little.

The narrow question is whether **GTM-specific prerequisite coverage improves supported Play proposals beyond generic hybrid retrieval, a domain prompt, and a domain-neutral coverage control**, under a common verified-event boundary and a fixed input-token allowance. Full context and an exact rules reference establish when retrieval specialization is unnecessary. Negative or conditional results are acceptable.

The domain model must not secretly give the proposed method cleaner information. All methods receive the same explicit facts, provenance, time/access metadata, catalog and public prerequisite vocabulary. The primary study isolates retrieval over verified events. It does **not** measure extraction from arbitrary documents, learned policy, business strategy quality, cross-company transfer, revenue or production Brain behavior. A larger end-to-end track is desirable only if it can actually be implemented and evaluated; do not imply it exists.

## Falsifiers and bias controls

- The prompt-specialized generic control matches or beats typed retrieval: domain structure has not demonstrated added benefit.
- A domain-neutral diversity control closes the gap: the useful mechanism is generic evidence coverage, not GTM specialization.
- Full context is best at the relevant record size: retrieval may only be a cost/length tradeoff.
- Retrieved support improves but executable, correctly cited proposals do not: memory quality has not translated into action support.
- Gains disappear on held-out prerequisite families or updates: the representation is brittle or tuned to fixtures.
- Always abstaining must fail on answerable cases. Report supported coverage, errors and abstention separately, with all attempts in the denominator.

Repeated queries and seeds are not new companies. Resample paired company-world means for uncertainty. Synthetic worlds share a generator; even company clustering does not make them independent samples from the commercial market. Vary task families, conditions, evidence layout and distractor composition and disclose the shared author/generator limitation. No fictional human annotation or strategic-usefulness score is permitted.

## Reuse decision

| Artifact | Decision and reason |
|---|---|
| Existing development harness | Retain all runs and tests; evolve a separately versioned main protocol. Its long UUID-heavy prompts and byte limits are unsuitable for a token-matched claim. |
| LongMemEval / V2 | Adopt label-blind input boundaries, temporal controls and a full-context reference. Do not repurpose conversational answers as GTM labels. |
| EnterpriseMem-Bench | Keep the executed scorer audit as methodology evidence. Do not copy permissive keyword scorers or use its one synthetic company as independent GTM data. |
| Hindsight / Graphiti | Attribution and architectural comparison; defer full extraction stacks because they would change backend, maintenance and inference budgets together. This limits conclusions to implemented adapters, not these products. |
| MemCompile | Adopt the need for complementary-evidence controls; no source copying while license is unresolved. LLM selection is not free and would require separate budget matching. |
| ielab/memory-systems-vs-rag | MIT code/license and pinned vendor manifest inspected. Reuse comparison design and the feasible Qwen3-Embedding-0.6B baseline; independently implement standard BM25/RRF/diversity in the small package. Do not claim upstream benchmark reproduction. |
| MemDerive / EviGraph | Cite direct conceptual overlap; implement original GTM fixtures and scorer because available artifact redistribution rights are not established. |
| Models/runtime | Apache-2.0 Qwen3-4B-Instruct-2507, Qwen3-Embedding-0.6B; MIT llama.cpp, all pinned and hashed. Third-party weight distributions remain downloads, not bundled release content. |

The generator, independent contract checker, prototype, raw model outputs, analysis and figure commands should be released together under the companion's explicit code/data licenses. Private source observations and planning remain outside the release manifest.

The model row records the initial feasibility choice. Subsequent development selected Qwen3-30B-A3B-Instruct-2507 Q4_K_M for the frozen study; the embedding model stayed unchanged. `release/TUNING.md` preserves the unsuccessful earlier readers and interface changes. The separately implemented Python and SQL contract checks share this research process and do not constitute independent human validation.

## Stopping the broad review

Ten query families, handoff seeds, backward references and newer counterexamples have been examined at documented depths. Additional closest work consistently narrows rather than supports broad novelty. Proceed to a small pilot and controlled study, while checking targeted references that affect design. This is a bounded critical review, not PRISMA-style exhaustive coverage. Remaining unreviewed candidates are retained in the search index, not quietly called exclusions.
