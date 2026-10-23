# Targeted benchmark-methodology review, 23 October 2026 UTC

This is a targeted extension of the completed v3 bounded search, not a restarted systematic review or a claim to cover every paper. The new request asks for more difficult model-style tasks. Inspecting these primary PDFs clarifies which design principles can transfer and which claims our benchmark cannot support. Download hashes and access outcomes are in `literature/challenge-fetch.json`; PDFs remain outside the public artifact. Review depth: selected methods/evaluation passages, not full-text/code reproduction. Bibliographic title/authors/version were checked on the PDFs.

## τ-bench, arXiv:2406.12045v1

Read introduction, task formalization, reward, construction and main experiments (§§1–5.2, pp.1–7). The benchmark evaluates interactive tool-agent-user behavior under domain policy, using a simulated user and database end-state checks. §3 explicitly says the binary reward can be necessary but insufficient for full policy compliance: a correct final database may hide missing user confirmation. §4 describes human task annotation and iterative validation; we do not have that authorship/annotation resource. §5 reports multiple trials and distinguishes pass^k (all k trials succeed) from pass@k (one succeeds). We must not call one response per case a reliability estimate.

Reuse: explicit policy constraints, deterministic checks, all-attempt denominators and separation of successful outcomes from complete policy compliance. Do not reuse the numerical leaderboard as a comparator: tasks, models, interaction and human construction differ. Our source-citation checks are narrower and our fictional generator lacks their manual task review. No code/data imported.

## AppWorld, arXiv:2407.18901v1

Read abstract/introduction and evaluation/validation/splits (§§3.2–3.4, especially p.6). Its state-based tests allow multiple valid solutions and check collateral database changes. Programmatic validation solutions verify task solvability. The challenge split holds out designated applications, which is stronger generalization evidence than changing our generator seed. Our new worlds do not constitute held-out task families or real-company generalization.

Reuse: evaluate feasible plans rather than matching one arbitrary answer; independently check an optimal reference; explicitly enforce duplicate-account/shared-budget constraints. We do not execute AppWorld tasks or claim equivalent difficulty. Our task outputs a plan, not an interactive coding agent operating hundreds of APIs. No artifact reuse/license claim is needed because no code/data was copied.

## τ²-bench, arXiv:2506.07982v1

Read introduction and programmatic task-construction section (§3.2, pp.5–6). Atomic initialization/solution/assertion functions compose verifiable tasks. The paper decomposes reasoning and communication through different control modes; this motivates separating evidence-recoverable value from reader-returned value, although these are different constructs. Increasing composed subtask counts provides a difficulty axis; our levels combine account count, distractors, conflicts and evidence allowance and cannot isolate those factors causally.

Reuse: compose explicit prerequisites and preserve a verifiable reference. Boundary: our shared current-view filter and clean relation fields remove extraction/interactive coordination problems present in richer agent settings. A difficult retrieval bottleneck is not proof of general model reasoning difficulty.

## Implication for the contribution

The useful contribution remains a controlled, inspectable context-selection experiment, with exact source requirements and a downstream constrained decision task. It is not a new frontier-model leaderboard or a novel claim that domain policy enables action. The primary v3 memory/marketing competitors (RAMP, Hindsight, Zep, Mem0, CMC, WiCER, MemoryArena and others) remain the relevant landscape. The query-word control is essential: if it yields the same inputs as a typed selector, the evidence supports task-aware retrieval/packing rather than an indispensable GTM-specific architecture. Preserve that potential falsification prominently even if the headline contrast against unconditioned company closure is large.
