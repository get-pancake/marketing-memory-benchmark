# Search log — current cutoff 22 October 2026 UTC

This is a bounded critical review, not an exhaustive systematic review. Network access to primary papers was restored during this session; the historical blocked-access record below is retained as provenance. No third-party model benchmark has been reproduced.

## Executed coverage

Ten arXiv first-page queries (maximum 50 results each) returned 423 occurrences, 399 unique records: agent memory evaluation; domain specific memory agent; temporal knowledge graph memory; memory planning recommendation; marketing agent memory; agent memory benchmark; truth maintenance case based reasoning; retrieval augmented generation long context; sales agent benchmark; knowledge based recommender. Exact URLs, retrieval times, titles and reparsed abstracts are in `search-results-2026-10-22.json`. The parser originally truncated highlighted abstracts; `scripts/screen_literature.py` corrected this from the archived HTML.

Title-keyword triage retains 179 potentially relevant occurrences as not deeply reviewed, marks 229 lower priority, and links 15 occurrences to selected primary sources. These are automated triage counts, not independent human inclusion decisions. The source bibliography also includes handoff seeds and citation/artifact discoveries outside those first pages. Screening false negatives and recency-biased first-page coverage remain possible.

Twenty-six research arXiv HTML/PDF pairs have canonical metadata and dated retrieval hashes; two additional model sources bring the arXiv bibliography total to 28. Critical full/main-text work covers RAMP, IFCMemoryBench, MARS, Hindsight, Zep, LongMemEval/V2, EviGraph, MemCompile, ReFind, controlled raw-history comparisons, RECON and AkasicMEM. Pre-results follow-ups expanded MemoryArena and Mem0 to their full main texts, with the appendices specified in their notes, and Anti-Persistence to its main text and selected appendices. AFTER/MemDerive/CRM/sales sections were reviewed selectively. Exact depth and omissions are in `reviews/`; not every appendix or cited paper has been read. The survey's taxonomy/benchmark overview and GraphRAG's abstract/introduction received narrower review.

Backward chains: EnterpriseMem references led to Mem0/LoCoMo and lifecycle baselines; Zep/Hindsight identify hybrid retrieval, source episodes and full-context controls; MemoryArena identifies interdependent action tasks and Mem2ActBench/MemTrack as further candidates; MemCompile and raw-history comparisons expose complementary selection and reader/retriever confounds. Forward discovery through LongMemEval's owner repository found V2; current-date searches found EviGraph, MemCompile, MemDerive and negative/controlled memory studies. This is targeted citation tracing, not an exhaustive forward-citation census.

Classical foundations: Crossref metadata verified Aamodt & Plaza's 1994 case-based reasoning article (10.3233/AIC-1994-7104), Doyle's 1979 truth-maintenance article (10.1016/0004-3702(79)90008-0), and Robertson & Zaragoza's BM25 review (10.1561/1500000019). An initially guessed Doyle DOI returned 404 and was corrected by a title/author query; it must not enter citations. Full classical texts remain an access/review gap. Crossref rate limits are retained, not bypassed.

Author-maintained artifacts: pinned README/license inspection for EnterpriseMem, LongMemEval/V2, Hindsight, Graphiti, GraphRAG; actual scorer execution for EnterpriseMem; actual scheduler source for MemCompile; controlled-memory comparison README, MIT license and vendored version manifest. A GitHub tree API request was blocked; the failed MemCompile LICENSE fetch does not establish absence of a license. No unlicensed code was copied.

## Decision and remaining coverage limits

At 2026-10-22T08:33:44.044388+00:00, selected original PDF tables/figures were visually checked for RAMP (page 5), IFCMemoryBench (pages 6–8) and MARS (page 8). The source numbers matched the reading notes; RAMP wording was clarified to distinguish eight evaluated human-study questions plus two practice questions, and the separate challenge experiment. Checks are recorded in `artifacts.json`; third-party page images remain excluded reading-cache material. No main quality outcomes were inspected.

At 2026-10-22T08:26:43.549049+00:00, a targeted artifact-link check inspected PDF annotations and visible URLs for RAMP, IFCMemoryBench and MARS. No attributable benchmark repository link was identified; IFCMemoryBench's Zenodo link names BayesProp rather than the benchmark. The annotation lists and source hashes are recorded in `artifacts.json`. This narrows the documented discovery gap without establishing that code is unavailable. No main quality outcomes were inspected. The comparison matrix now includes the expanded Mem0/Anti-Persistence reviews and an explicit artifact-inspection column group.

Targeted review at 05:24–05:30 UTC, before main outcome inspection: Mem0 v1 was expanded from screening to the full main paper and appendices, with current pinned owner/core and benchmark README/license checks. The current ADD-only hybrid platform differs from the 2025 extraction/update paper; no hosted claims or model results were reproduced. More Memory, Worse Agents v1 was expanded to full main text and selected methodological, cost, provenance, sensitivity and limitation appendices. Its qualified observational reproduction argument is not a causal proof or a universal rejection of persistent guidance. See `reviews/mem0.md` and `reviews/anti-persistence.md`. This follow-up changed no frozen experimental method or protocol.

Targeted MemoryArena expansion during frozen main inference, 04:55–05:04 UTC: read the full main paper and selected A.2/B.1/C.1–C.3 appendices, without inspecting main experiment quality outcomes. Verified ICML 2026 publication using PMLR volume 306 and its owning article page; downloaded the publisher PDF and checked that normalized construction, main experiments and implementation sections match arXiv v2. The proceedings title omits the arXiv metadata's “MemoryArena:” prefix. Venue/title provenance and unresolved reproduction details are recorded in `reviews/memoryarena.md` and `sources/verified-venue-metadata.json`. This is a bibliographic/review-depth update, not a change to the frozen experiment.

Targeted foundation/venue check during frozen main inference, 22 October 2026 04:22–04:25 UTC: OpenAlex DOI records located institutional copies for Doyle (MIT handle 1721.1/5733) and Aamodt/Plaza (CSIC handle 10261/160159). These discovery records were retrieved and hashed, but the institutional pages remained blocked by the current network policy, including after an automatically approved read-only retry. They were not read or used as full-text evidence. BM25's indexed record supplied no open full-text location. The pinned LongMemEval README reports ICLR 2025 acceptance; the official OpenReview API request returned 403, so acceptance is not independently verified here. A saved environment draft adds the institutional hosts, but requires publication and did not change current access. None of these checks changes the frozen experimental design.

`GAP_AND_REUSE.md` narrows the contribution to a controlled GTM Play-contract study. Evidence-backed recommendation, derived-state maintenance, temporal provenance and complementary retrieval are already prior art. The broad review stops here to permit actual experiments, with targeted checks continuing. Remaining limits include full classical texts, comprehensive citation indexing, all candidate abstracts/full papers, independent human reviews and reproduction of large-model systems. The paper must disclose these limits and avoid a first-ever or state-of-the-art claim.

# Historical search checkpoint, before access was restored

Search date: 2026-10-21 (America/Los_Angeles); retrieval receipts use UTC.

## Coverage and limitations

This is an ongoing critical review, not a completed systematic review. Scholarly-index and arXiv requests are blocked by the current network policy. GitHub is available for author-maintained artifacts; repository search is supplementary discovery, not a substitute for paper/citation search. No numerical study result has been independently reproduced.

| Family | Executed work | Remaining work |
|---|---|---|
| Agent memory | LongMemEval, Hindsight, Graphiti artifact inspection; followed LongMemEval README to V2 | Full papers, survey and citation chains |
| Domain specialization | EnterpriseMem-Bench full manuscript/source inspection; IFCMemoryBench repository-name search | IFCMemoryBench paper and professional-domain comparisons |
| Temporal/relational knowledge | Graphiti documentation, enterprise temporal scorers; RECON and AkasicMEM repository search | Full papers, provenance and belief-revision foundations |
| Knowledge to action | Hierarchical belief-memory repository search; LongMemEval-V2 discovery | Full recommender/planning papers |
| GTM/marketing | RAMP title/identifier repository searches | RAMP full paper, marketing planning and audience curation |
| Evaluation | Enterprise scorer audit; LongMemEval protocols and dataset version changes | Judge reliability, contamination and independent tests |
| Classical foundations | No primary full text reviewed yet | Case-based reasoning, truth maintenance, knowledge-based recommendation |

## Executed source requests

Every cached retrieval is recorded in `retrievals.jsonl` with URL, UTC retrieval time, byte count and SHA-256. Downloaded texts stay in ignored `.cache/literature/` because redistribution rights vary.

- Initial `https://arxiv.org/abs/2508.11120`: proxy tunnel HTTP 403.
- Initial official Goal documentation: proxy tunnel HTTP 403.
- Read-only Git HEAD probes succeeded for EnterpriseMem-Bench, LongMemEval, LongMemEval-V2, Hindsight, Graphiti and GraphRAG. Pinned revisions are recorded in `artifacts.json`.
- GitHub identifier searches `2508.11120 in:readme` and `2607.26072 in:readme` returned largely irrelevant numeric-token matches. Excluded those hits; absence of a relevant hit is not absence of code.
- GitHub repository-name search `IFCMemoryBench`: zero hits. `"Agentic Recommender" "Belief"`: zero hits. `"AkasicMEM"`: zero hits. Full-paper artifact links remain to be checked.
- `RAMP marketing`: 15 repository hits; visible first-page matches concern unrelated launch-marketing tools and personal marketing sites. No source attributable to the seed paper was identified.
- `"RECON" "agent memory"`: two repository hits, neither yet authenticated as the seed paper companion. Do not reuse their descriptions as paper evidence.
- Backward references from EnterpriseMem-Bench identify LOCOMO, CRUD-RAG, MemGPT, Mem0, LangMem and EverMemOS as further candidates. Metadata in its bibliography is not independently verified.
- Forward artifact chain: the LongMemEval README links a May 2026 V2 release; read its owner-maintained README and add it to priority screening.

## Inclusion rules

Prioritize primary studies that evaluate memory under changing evidence and connect retrieved knowledge to decisions/actions, or expose reusable evaluation controls. Include strong simple/full-context baselines and negative findings. Exclude unrelated products with the same acronym. Record abstract-only, README, code, full-text and reproduced states separately. A reported venue is not independently verified until checked with the owning proceedings.

Targeted classical-author access check, 12:01 UTC, before main outcome inspection: the public NTNU Agnar Aamodt and Waterloo Gordon Cormack homepages were attempted as primary-source discovery routes. Both returned proxy tunnel403. Retrieval receipts are retained; no additional full-text review or source-content claim follows. Existing classical access gaps remain explicit.


## Integrated-report amendment,22–23October2026UTC

Six further arXiv API families (marketing memory, context compilation, structured-file memory, enterprise next action, domain memory and memory versus retrieval) returned115 occurrences/113 unique identifiers; previous search overlap is retained, not counted as additional reviewed papers. Exact queries/results: `integrated-search-2026-10-22.json`; public metadata-only index: `release/literature-integrated-index.json`. Read important methods/results in WiCER, CMC and VehicleMemBench at the depths recorded in `reviews/integrated-memory-wiki.md`. Reviewed actual provider model lists/prices, GBrain's pinned component, and an MIT community Karpathy-style wiki workflow. The user confirmed GBrain and Karpathy's Markdown approach. Direct primary Gist access remains403; community descriptions are not unqualified primary attribution. Stop the renewed broad pass after these targeted comparisons sharpen the fixed-reader study; continue targeted checks while executing. No claim of exhaustive coverage, independent screening or reproduced third-party headline scores.
# Targeted challenge extension — 2026-10-23 UTC

Following the user's harder-benchmark/Opus request, directly retrieved primary PDFs for τ-bench (2406.12045v1), AppWorld (2407.18901v1) and τ²-bench (2506.07982v1). This is a purposive methodology check, not a new exhaustive database search or an added independent literature sample. Selected task-construction/evaluation sections were read; code was not reproduced. Stable citations and hashes: `challenge-fetch.json`; critical notes: `reviews/challenge-benchmark-methodology.md`. These works motivate explicit constraints, acceptable alternative plans, independent executable references and clear distinctions between fresh worlds, held-out task families and repeated-trial reliability.

