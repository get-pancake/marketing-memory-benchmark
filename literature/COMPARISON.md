# Critical comparison matrix

Updated 22 October 2026. All literature numbers are source-reported unless explicitly labelled our executed audit. Exact reading depth and limitations: reviews/. Public metadata and artifact pins: release/literature-index.json and artifacts.json.

| Work | Task/domain knowledge | Change and provenance | Action evaluation | Implication for this study |
|---|---|---|---|---|
| RAMP | Marketing audience curation; client facts and prior queries | Semantic/episodic memory, reflection | Planner/tool/verifier output; small PM assessment | Direct memory-to-marketing prior art; do not allow implicit relaxation of hard policy |
| IFCMemoryBench | BIM context + live structured-model queries | Project conversations, fragmented facts | Tool-assisted answers, model judges with expert subset | Domain prompt changes can help or hurt; strong evidence for prompt-only control |
| MARS | Consumer recommendation, event/preference/profile hierarchy | Heuristic belief strength and lifecycle operations | Retrospective ranking and simulated evolution | Not calibrated confidence or business Play ROI |
| EviGraph | Temporal public-service recommendation | Scoped evidence, critical obligations, proof checking | Recommend/verify/exclude under generated policy labels | Proof-supported recommendation is prior art; count coverage as well as error |
| Hindsight | Facts/experience/opinions/observations | Retain/recall/reflect, temporal/source structure | Mainly QA | Rich generic memory already has these concepts; construction/reader budgets matter |
| Zep / Graphiti | Entity/episode/community memory | Bitemporal facts, sources, invalidation | DMR/LongMemEval QA | Hybrid/temporal retrieval is established; small full-context controls can match |
| LongMemEval / V2 | Conversation / agent-trajectory memory | Updates, abstention, dynamic state, gotchas | QA; V2 procedure and premise awareness | Adopt causal label-blind boundary; cross-track controller changes confound attribution |
| MemCompile | Query-conditioned source-packet compilation | Source-normalized evidence, selection and rendering | Long-term QA | Complementary coverage is prior art; count selection retries and actual tokens |
| ReFind | Agentic raw-chat search | Session expansion, temporal filters | Multi-benchmark QA | Raw-history and competent search are strong controls; ingestion savings shift query cost |
| Explicit memory vs raw history | Six memory systems, raw granularities, retrieval/budget grid | Frozen stores and provenance oracles | Shared-reader QA | Retriever choice can reverse conclusions; avoid best-of-test configuration selection |
| RECON | Evolving criminal/medical/financial cases | Deterministic provenance DAGs, invalidation and alternate supports | Compositional answers, human/model grading | New GTM nouns do not make provenance reasoning novel |
| MemDerive | Symbolic evolving scenarios and derived state | Datalog gold/witnesses, refresh/preservation | Answers plus intermediate-state diagnostics | Closely overlaps our diagnostics; report incremental GTM contract contribution |
| AkasicMEM | Governed enterprise memory | Transitive lineage and current authorization | Proposed evaluation, not demonstrated outcome quality | Architecture requirements are not empirical performance guarantees |
| AFTER | Workplace procedural skills | Trace-based refinement, skill versions | Executable test success and transfer | Source gains need not transfer across roles; hold out families |
| EnterpriseMem-Bench | Synthetic enterprise lifecycle QA | Temporal/versioned facts | Keyword/number scoring | Our scorer counterexamples reproduced; not its model findings |
| Sales Research Bench | Sales analysis and charts | Enterprise schema grounding | Weighted model-judged composite | Different access/backbones confound a memory-only conclusion |
| CRMArena-Pro | CRM business workflows | Role/context, confidentiality | Task execution + simulated dialogue | Prompt policy matters; neither model judge nor simulated customer is real outcome evidence |
| MemoryArena | Interdependent shopping/travel/search/reasoning | Memory-action-feedback loops | End-to-end multi-session success | Already connects memory to action; our one-step research Play is narrower |
| Mem0 | Conversational fact extraction and retrieval | Update/delete operations; optional relational memory | LoCoMo answers with model judging | Historical base/graph budgets differ; current software is not the evaluated 2025 release |
| Anti-Persistence | Task guidance derived from prior trajectories | On-demand synthesis without retaining abstractions | Iterated task success and observational provenance diagnostics | Error propagation is a qualified hypothesis; our stateless queries cannot evaluate the feedback loop |
| GraphRAG | Global corpus sensemaking | Extracted communities and summaries | Model-judged summary quality | Different task from bounded prerequisite selection; no blanket graph advantage |

Reuse and falsification decision: GAP_AND_REUSE.md. The prototype compares small explicit adapters on one backend, not full reproductions of these systems. No graph database is necessary for the selected experiment.

## Artifact inspection boundary

The rows below distinguish inspected artifacts from papers that describe a system. Exact repository revisions, licenses and inspection depth are in `artifacts.json`; reading an artifact does not reproduce its model results.

| Work(s) | Artifact evidence inspected | Reuse/reproduction boundary |
|---|---|---|
| EnterpriseMem-Bench | Pinned manuscript, README, licenses, scorer modules and a ten-item fixture subset | Deterministic scorer probes executed; system/model results not reproduced |
| LongMemEval / V2; Hindsight; Zep / Graphiti; GraphRAG | Pinned owner README/license material, with exact review depth in the artifact register | No complete system runs; GraphRAG full paper/code review remains incomplete |
| MemCompile | Pinned README and packet scheduler | License unresolved; no implementation copied or model run |
| Explicit memory vs raw history | Pinned README, MIT license and vendor-version manifest | Comparison design informs our controls; its benchmark was not reproduced |
| Mem0 | Pinned current core and benchmark READMEs and Apache-2.0 licenses | Current hosted/OSS pipeline is distinct from the historical paper; no hosted calls or benchmark execution |
| RAMP; IFCMemoryBench; MARS | Full papers and PDF link annotations checked; initial repository discovery documented | No attributable benchmark code/data license established; absence of a discovered link is not proof of unavailable code |
| EviGraph; RECON; MemDerive; AkasicMEM; AFTER; ReFind; Sales Research Bench; CRMArena-Pro; MemoryArena; Anti-Persistence | Paper methods and artifact statements at the depths recorded in `reviews/` | No versioned implementation/license audit or model reproduction claimed; no source/data copied |

The PDF annotation check on 22 October 2026 found no attributable benchmark-repository link in the reviewed RAMP, IFCMemoryBench or MARS PDFs. IFCMemoryBench's Zenodo citation is BayesProp statistical software, not its benchmark release. These are bounded discovery findings. Artifact-access gaps remain explicit rather than being replaced with an invented reproduction claim.
