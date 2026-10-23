# Better company context, more grounded recommendations

**Research companion · 23 October 2026**

Company memory can improve recommendations by delivering the evidence an action requires. Our experiments support that mechanism: with the same GPT or the same Claude, prerequisite-aware selection raises correctly grounded decisions from **84.5% to 100%** on a controlled marketing benchmark. The gain is **15.5 percentage points**, with a company-clustered 95% interval of **9.8–21.2 points**. This is a measured improvement in evidence-backed eligibility decisions, not a forecast of revenue growth.

## What we tested

The main study contains 33 newly generated fictional company worlds and 264 cases, evenly divided between cases that support an action and cases that require withholding. It compares seven context treatments with GPT-6.1 Sol and Claude Sonnet 5.5: **3,696 actual provider calls**, all retained. Within each reader, prompts, action catalog and output settings are fixed. Bounded methods receive the same 2,048-byte evidence allowance. The cases cover renewal, partner and compliance workflows; these task families were known during development.

| Context supplied to the same reader | Grounded decisions, each model |
| --- | ---: |
| No company context | 132/264 (50.0%) |
| Generic hybrid retrieval | 223/264 (84.5%) |
| Structured Markdown with generic coverage | 264/264 (100%) |
| Native GBrain search component | 152/264 (57.6%) |
| Marketing prerequisite coverage | 264/264 (100%) |
| GBrain plus prerequisite coverage | 264/264 (100%) |
| Full current company context | 264/264 (100%) |

Both readers withhold appropriately on all 132 negative cases. The improvement comes from recovering missing support: **132 supported recommendations versus 91**, or **45.1% more supported recommendations** on the positive cases. The no-context result reflects missing information, not a defect in the models.

## The strongest architecture finding

Coverage matters more than the storage label. A strong domain-neutral Markdown selector and GBrain augmented with the same coverage module match specialization at the main budget. Native GBrain search here is one pinned retrieval component, without its full ingestion, graph and reranking stack; this is not a whole-product ranking.

Under a tighter 1,024-byte allowance, specialization retains all required support in **132/132** positive cases, compared with **52/132** for structured Markdown. This is a retrieval-only diagnostic: we did not run a second recommendation experiment at that budget. At larger allowances, generic methods catch up. The defensible thesis is that action-aware context selection can improve efficiency and usefulness under constraints, not that every specialized brain beats every general brain.

<!-- pagebreak -->

# What to build, and what the evidence does not establish

## A practical product direction

Represent approved strategy, external observations and proposed actions separately. Make an action's prerequisites explicit. Select current, permitted evidence that covers those prerequisites; attach sources and policy versions; validate eligibility and resource limits before execution. This mechanism can sit above files, retrieval or a company-memory platform.

The main comparison isolates selection over verified records. It does not measure the cost of extracting those records or maintaining them. The deterministic reference solves all formal cases without a model, so an LLM is not necessary for this exact eligibility problem. The useful engineering question is where language understanding helps before and around those checks.

## What messy documents reveal

A separate exploratory study uses 118 publicly licensed fictional company documents, 22 upstream development questions and 264 actual reader calls, including a post-hoc chunked-retrieval control. A question-blind compiler produces general and marketing-oriented Markdown wikis from the same sources.

GPT scores 22/22 with the marketing wiki, versus 21/22 with the general wiki, full documents and chunked retrieval. Claude scores 20/22 with either wiki and 21/22 with full documents or chunked retrieval. Removing one ambiguous question erases GPT's one-answer specialization advantage. Compilation can omit a dated detail or preserve conflicting role descriptions; the qualitative review traces these failures to sources. This small, already inspected development set does not establish general wiki superiority or independent human validation.

## Resources and reproducibility

The main provider-usage estimate is **$33.99**. Specialized packets use **31.7% fewer GPT input tokens** and **28.4% fewer Claude input tokens** than full context, with the same observed decisions. These are input reductions, not guaranteed total-cost savings. Across provider pilots, compilation and reader experiments, known usage is approximately **$55.49**; three unsuccessful attempts lack usage receipts. Hardware, curation and unknown charges are excluded, and estimates are not invoices.

The companion includes code, licensed data, prompts, raw provider responses, failed development attempts, analysis and vector figures. Its offline reproduction recomputes the saved evidence; fresh inference is a separate paid operation. A mock executor checks 1,278 supported proposals using fictional capabilities and makes no external actions. Neither mock execution nor eligibility scoring measures strategic usefulness, outreach response or revenue.

For Pancake, the evidence supports a focused investment in evidence coverage, provenance and explicit action prerequisites. It does not establish customer retention, a moat, network effects or commercial lift. Independent practitioners and real operational outcomes are the next validation layer. The working repository remains private; the clean companion is prepared for a separate public release. This AI-assisted technical report is not peer reviewed.
