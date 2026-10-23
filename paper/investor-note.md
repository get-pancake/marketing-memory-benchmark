# Better context before a more complex brain

**Evidence from a controlled marketing-decision study — 23 October 2026**

The measured result is clear: selecting evidence around the decision task substantially improves grounded recommendations under a limited context allowance. The same experiment also shows that a well-designed generic selector can reproduce the specialized context. The supported investment is task-aware evidence selection and validation; a separate proprietary memory architecture is not demonstrated as necessary.

## What we actually ran

The new main study uses **120 fictional company worlds, 360 multi-account cases and 4,320 actual GPT-6.1 Sol / Claude Opus 5.5 responses**. Each case asks the model to choose up to three actions under a shared resource budget. It must connect policy, account observations, buyer need, offering, proof and action-specific approvals. Three stress levels increase the account set and distractions while reducing the evidence allowance. The dataset and methods were frozen before main generation.

The score measures the fraction of achievable **synthetic policy-priority value** returned in a feasible plan with all required citations. It is not revenue, conversion rate or an expert's opinion of strategic quality. There are 288 positive cases; 72 cases with no feasible action are scored separately for safe abstention.

| Context supplied to the same reader | GPT-6.1 Sol | Opus 5.5 |
| --- | ---: | ---: |
| No company evidence | 0.0% | 0.0% |
| General company context | 47.9% | 47.9% |
| Task-aligned GTM context | **88.4%** | **88.2%** |
| Full current context, larger allowance | 100.0% | 98.1% |

GTM gains **40.6 percentage points** over Company for GPT (95% company-bootstrap interval 36.7–44.4) and **40.3 points** for Opus (36.3–44.3). No company evidence cannot support company-specific decisions under this contract; its zero is an information reference, not a general model-capability score. All treatments abstain correctly on the 72 negative cases for each reader.

## Why it matters for product design

Most lost value comes from evidence that never reaches the reader. Both readers recover the context-supported optimum on every Company positive case. Better evidence selection therefore deserves its own product metric, alongside answer quality. The practical pattern is a durable company record, task-aware retrieval, explicit dependencies and a validator that requires the sources needed for each proposed action.

<!-- pagebreak -->

## The boundaries are part of the finding

**A strong generic control matches the specialized inputs.** A selector using words in the shared task query produces exactly the same ordered context as the GTM selector on all 360 cases. Its displayed results alias those inputs; it adds no independent model observations. The experiment supports a useful selection mechanism, not an exclusive architectural advantage.

**More generic context can close the gap.** In a retrieval-only sweep, GTM recovers all formal value at 16 KiB, while Company reaches 98.5% at 64 KiB and 100% at 128 KiB. These alternate-budget figures measure available evidence, not additional reader experiments. In the actual main runs, full context performs better and costs 2.63 times GTM for GPT and 2.27 times for Opus in reader usage.

**External documents give a counterexample.** On 22 development questions from one externally authored fictional company, the general wiki yields 22 correct Opus answers and the marketing wiki 21. This 132-call extension uses actual raw documents and previously compiled query-blind wikis. It is small and exploratory, but it prevents a claim of universal specialization superiority.

**Justification quality differs from decision quality.** Nine Opus plans have a required citation defect despite selecting actions that otherwise attain the available-context optimum. Two GPT plans are slightly suboptimal. Removing citation-binding checks in a disclosed sensitivity brings Opus to 88.4% with GTM and 100% with full context. Primary scores retain the strict evidence requirement.

## Cost, release and next evidence

Main reader usage is estimated at **$147.68**. The complete new study, including development, availability checks, embeddings and the external Opus extension, has known usage of **$183.66**. These are token-usage/list-price estimates, not invoices or production ownership costs. Data ingestion, curation, maintenance, infrastructure and practitioner time are excluded.

The companion contains licensed code/data, every releasable request and response, reference solvers, scoring, company-clustered uncertainty, figures and LaTeX. Saved-output reproduction is tested separately from fresh paid inference. GBrain is evaluated as a pinned search component; this is not a ranking of whole commercial products. The Markdown implementation is an original pattern, not an official Karpathy product.

The next product milestone is independently authored raw company histories and blinded practitioner evaluation of proposed actions, followed by prospective business outcomes. The current evidence justifies measuring and improving evidence completeness and context efficiency. It does not establish customer retention, a network effect, revenue lift or commercial defensibility. The working repository remains private; public release and paper submission are separate steps.
