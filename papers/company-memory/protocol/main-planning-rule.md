# Prospective main-study planning rule

Recorded during Stage B, before inspecting its completed results and before generating main worlds or obtaining any held-out model output.

The main estimand is the paired company-world mean difference in supported-decision accuracy between catalog coverage and prompt-specialized hybrid retrieval. Each world supplies the same eight positive/negative, stable/update conditions. A single deterministic decoding setting is used; repeated questions or seeds do not enlarge the independent world count.

Planning precision: aim for a 95% interval half-width of approximately 0.15 in absolute accuracy for the primary difference, conditional on this fictional generator. Two pilot worlds provide an unstable variance estimate, so use the larger of the observed paired-world SD and 0.20 as an explicit heuristic planning floor. This is not a worst-case bound or an assertion that the achieved interval will meet the target. For N >= 12, use 2.202 as a conservative t multiplier in `2.202 * planning_SD / sqrt(N)`. Choose at least 12 worlds and round upward to a multiple of the three held-out families. Report the actual bootstrap interval irrespective of its width or sign.

Estimate serial CPU time using measured pilot latency, including the longer full-context calls. If this sample is infeasible in the actual environment, record a concrete resource/precision amendment before generating the main data; do not silently reduce N after observing main outcomes. No paid API budget or persistent-Goal token budget is inferred from this planning rule.

Use independent main seed 2026102202, distinct from development seed 2026102201. All worlds and query/template-family splits must be generated and hashed at the freeze, not selected for favorable outcomes. Freeze source, model/runtime, dataset, method list, input/output caps, order seed and analysis plan before main execution. The source-defined noise levels cycle 12/20/28/36 and duplicate pairs are independently randomized, with family and nuisance-factor distributions reported.

Primary comparison uses the common 1,024-token input cap developed for contract feasibility. A larger-cap sensitivity comparison is valuable to expose whether any advantage disappears when context is less scarce; select its exact scope and resources before the main freeze. Full context remains a separately costed reference. None of these counts or targets is an experimental finding.
