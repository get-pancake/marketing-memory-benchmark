# MemoryArena: closed-loop action is a stronger claim

Targeted review expanded on 22 October 2026 during frozen main inference, before inspecting main quality outcomes. No experimental design changed. Source: arXiv **2602.16313v2**, dated 17 September 2026. The owning PMLR record independently verifies ICML 2026 publication as **“Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks,”** volume 306, pages 41975–42005: <https://proceedings.mlr.press/v306/he26am.html>. Its publication metadata date is 29 September; the conference dates are 6–11 July. These are different dates, not conflicting submission times.

The proceedings title omits the arXiv metadata's “MemoryArena:” prefix. The bibliography now uses verified proceedings metadata and preserves the consulted arXiv version. The publisher PDF was retrieved and hashed; normalized task-construction, main experiment and implementation-appendix sections match the reviewed arXiv text exactly. The retrieval ledger records both versions. This verifies publication/content provenance, not reproduction of the reported model results.

**Depth:** full main text through conclusions and impact/limitations; Appendix A.2 shopping construction, B.1 retrieval-frequency statement, B.1.1–B.1.3 runtime protocols, C.1–C.3 additional models/latency/diagnostics. The full prompt panels, many individual examples and the long C.4 case-study appendix are not comprehensively reviewed; code/data were not executed and artifact redistribution licenses were not established here.

## What it already addresses

The benchmark deliberately couples memory updates to interdependent actions and environment feedback. Its four environments cover bundled shopping, group travel, progressive search, and formal reasoning (math/physics reported separately). Main Table 2 gives 150/270/221/40/20 task groups, totaling 701; the paper reports 4,850 subtasks. These are not independent samples when subtasks share a trajectory. Shopping chains and travel constraints are constructed and manually checked; formal reasoning uses expert-curated derivation chains. This is substantially richer than our stateless one-step contract queries over verified records.

The search subset removes original BrowseComp-Plus instances solved in one interaction, then decomposes and human-checks retained queries. That makes memory dependence an explicit selection condition, not evidence that its case frequencies represent ordinary search. Shopping selects large product categories and injects price/rating preferences to make one choice unique. Such design choices are legitimate controls but define the population being tested. Our task instead accepts multiple eligible catalog alternatives and does not assert unique commercial utility.

Main Table 3 compares long context, external memory and RAG with a shared task-agent claim, and includes several long-context backbones. Soft constraint progress, complete-subtask progress and task success are distinct. Shopping/travel success requires a globally valid bundle/plan; search/formal reasoning success is the final answer. The printed “All Task Avg SR” averages the five reported domain columns, rather than weighting every one of the 701 task groups equally. Do not call it pooled task accuracy without recomputing the weights.

## Adversarial reading and reproduction requirements

- Exact backbone identity needs artifact verification: the main prose says GPT-5-mini while Table 3/4 rows and caption use GPT-5.1-mini. We do not resolve this inconsistency by inventing an identifier or claiming access to that endpoint.
- Appendix B.1 says retrieval occurs once at the beginning of each subtask; B.1.1 describes injection before each decision. The serving implementation/configuration must establish the actual retrieval frequency before reproducing cost claims.
- The table does not support a universal rule that every external-memory configuration is slower than every long-context configuration. There are exceptions in individual cells. Paradigm-level averages and particular method comparisons must remain separate.
- The Appendix C.3 prose says dependency success eventually drops to zero, but its Table 7 values end at **0.15** at L4. Do not repeat the stronger prose claim. These are conditional constraint rates, not independent task accuracy estimates.
- The approximate-oracle intervention adds golden prior outcomes **and LLM-distilled workflows**. It changes more than fact recall. Its remaining errors support a utilization bottleneck but do not isolate a pure retrieval effect or a calibrated belief-state error.
- Temperature zero is described as guaranteeing reproducibility in the formal-reasoning protocol. It does not guarantee cross-runtime/provider determinism. Raw outputs, model revisions and actual request accounting remain necessary.
- Main comparisons involve complete heterogeneous memory systems, not a matched ingestion/query-token experiment. Their differing representations, model operations and budgets prevent attributing a ranking solely to graph structure or domain semantics.

The reported setup uses official OpenAI, Anthropic and Vertex APIs, with H100 GPUs for components requiring GPU execution. The appendix explicitly notes substantial API cost for full multi-system evaluation. We have not reproduced these runs, borrowed their numerical results as our own, or copied their implementation.

## Consequence for this report

Memory-to-action and interdependent agent memory are already established evaluation directions. Our narrower experiment can isolate how a public prerequisite catalog changes evidence selection under a fixed reader-input allowance. It cannot claim closed-loop skill acquisition, autonomous belief-state learning or multi-session agent planning. The common SQL reference, input-capacity diagnostic and available-support versus utilized-support measurements make that limited boundary inspectable. A future end-to-end study would need independent histories, actual memory writing and interdependent actions; additional static queries would not establish those capabilities.
