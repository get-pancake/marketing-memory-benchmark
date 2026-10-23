# More Memory, Worse Agents: a useful counter-hypothesis

Expanded 22 October 2026 while frozen main inference was running, before inspecting its quality outcomes. Source: **2610.27406v1**, 19 October 2026, *More Memory, Worse Agents: Error Reproduction and Anti-Persistence in LLM Agents*, Ruhan Wang, Kishan Panaganti and Dongruo Zhou. Status: preprint; metadata/PDF retrieval hashes retained. All numerical observations below refer to that source, not our experiment.

**Depth:** full main methods/results and conclusions, Appendix A's definitions/proposition, B.1/B.3–B.5 implementation protocol, D experimental setup, E.2/E.3 cost/provenance audit, F auxiliary/statistical analyses, G budget sensitivity and H limitations. Some prompt panels, individual examples and plotted curves are not comprehensively audited. No implementation or model results were reproduced; an attributable versioned code/data license has not been established.

## Mechanism and comparison

The method retains trajectories/outcomes while synthesizing task-specific guidance on demand and discarding that guidance afterward. Its controller chooses direct reuse, imitation, strategic or corrective modes with a similarity/recency-weighted UCB-inspired heuristic, warmup and exploration. The authors explicitly do not claim a confidence-bound or regret guarantee. Temporary guidance can still influence later records and synthesis: absence of stored abstraction objects does not mean absence of feedback.

The main study uses ALFWorld, WebShop and ScienceWorld with three backbones, ten memory-update iterations and three seeds. Training episodes alone update memory/controller state; evaluation freezes both. Appendix D specifies 134/100/60 held-out tasks, with WebShop and ScienceWorld splits differing from some prior benchmark protocols. Three random seeds are repetitions of those task populations, not three new datasets. Table 1 averages cannot be transplanted to different published splits.

The main comparison changes more than persistence: task-conditioned synthesis, retrieval modes and adaptive selection differ. The persist-versus-discard ablation in Table 2 is closer to the claimed mechanism and reports setting-dependent benefits. AutoRefine is explicitly adapted with different retrieval and synthesis; its ranking does not isolate maintenance quality or show that all maintenance is ineffective.

## What the evidence does and does not establish

- Table 1's equal-weight aggregate favors anti-persistence, but it does not win every model/task cell. Gemma's joint-memory ScienceWorld result exceeds it; Reflexion is higher on Gemma/ALFWorld. This supports a conditional hypothesis, not a universal rule against abstraction.
- Table 6 counts execution/synthesis calls per held-out task. It does not measure total tokens, elapsed latency, embedding cost, training/maintenance amortization or dollars. A call may contain very different context lengths. Lower average call count does not establish matched-total-cost superiority.
- The abstract's “error reproduction” story is qualified by Appendix E.3: parent–descendant flags are observational associations, and its aggregates were not recomputed/verified against event-level provenance and labeling-eligibility logs for that revision. Group counts and uncertainty procedures are unavailable. Retrieval of a skill may concentrate on difficult tasks, so a lower success rate among exposed episodes is not evidence that the skill caused failure.
- Appendix A's proposition is a conditional-probability decomposition, not a demonstrated positive lower bound under every maintenance policy, a causal transmission coefficient or proof of inevitable long-run error growth. The anti-persistence guarantee is narrowly the absence of stored abstraction objects; temporary errors and indirect feedback remain possible.
- Appendix F's useful/toxic skill experiments and selective-retention study retain only aggregates, without task/seed observations for uncertainty. The AppWorld percentages cannot be reconstructed as exact integer successes on 30 tasks from the provided data alone. They test immediate effects of supplied content or a frozen retained layer, not multigeneration error reproduction.
- Table 7's tests use rounded means from nine fixed benchmark/backbone cells. Shared models and benchmarks make these dependent settings; Holm adjustment does not correct that dependence or create population inference. The paper itself calls these exploratory summaries. They are not substitutes for paired task/trajectory analyses.
- All tested defaults win their displayed sensitivity sweeps, but this does not establish an optimum outside those values or resolve tuning-selection uncertainty. The reported neighborhood threshold was chosen on a small validation set; its exact composition and full tuning effort need artifacts before replication.

## Relevance to Pancake

The work strengthens the requirement to distinguish observations, inferred guidance and approved policy. A non-response must not silently become a universal exclusion. It also supplies a serious counter-hypothesis: retaining more derived guidance can add error and cost, while selecting raw evidence afresh may suffice.

Our study does not perform experience-driven learning or re-abstraction; its weak-feedback and supersession cases test a declared contract on static histories. They therefore cannot confirm or refute the paper's feedback mechanism, demonstrate calibrated beliefs, or establish successful contextual-bandit learning. A later Pancake learning study would need actual independent outcome histories, admissible update rules and controlled persistence interventions. The present report remains an evidence-selection experiment.
