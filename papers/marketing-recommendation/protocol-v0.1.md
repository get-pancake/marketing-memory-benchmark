# Paper B — evidence-grounded next-action recommendation

Status: prospective protocol and pilot interface, not model results. Dated 22 October 2026.

## Question and isolation

Given identical current company context, objective, constraints and action capabilities, does explicit evidence binding and constraint validation improve useful next-action recommendations over a strong direct model baseline? Memory retrieval is held fixed. "Next best action" is the product ambition; eligible, useful, preferred and revenue-optimal are different claims.

The explanatory matrix is **two reasoning backbones × two recommendation methods**: one versioned Claude model and one versioned GPT model, each used (1) directly with a strong common domain prompt and (2) inside the proposed method. Use exact available API identifiers and capabilities, rather than claiming an unspecified "Claude" or "GPT" result. Do not compare our system plus private information to a context-free chatbot.

## Pilot made concrete

Use 16 existing development queries (two fictional worlds × eight conditions), selected by stable ID from `data/study/pilot-v5`. Four cells give **64 planned provider requests**, with at most 4,096 input tokens and 768 output tokens per request. This is an execution/competence pilot on known synthetic rules, not a main scientific sample or an independent marketing benchmark. All arithmetic is a proposed cap, not observed usage. At these caps the pilot envelope is 262,144 input and 49,152 output tokens across both providers.

Both methods receive byte-identical evidence, objective and full catalog. The direct baseline receives all hard constraints, domain instructions and a request for source bindings. The proposed prompt additionally asks for candidate-by-candidate prerequisite checks before choosing, rather than taking a union of unrelated candidates' requirements. Both prompts use the same final output schema. This is a disclosed scaffolding intervention, not a different memory. Apply deterministic post-validation to **both** arms as a further matched control; rejected proposals remain an explicit abstention/failure for useful coverage. The validator does not secretly replace the model with the ground-truth answer. Count raw and post-validation quality separately. No repair loops in this first pilot, avoiding extra uncharged model calls. Future prompt/tool revisions are new method variants.

Each saved model proposal is evaluated before and after validation without another paid call: at most 64 physical requests yield 128 raw/validated logical evaluations. These are not independent generations. Separately report the prompt intervention, validation intervention and their interaction; do not attribute validator-only gains to novel strategic reasoning.

Fresh model access requires separately configured credentials, reachable official API domains, a user-approved USD cap and verified price rates. No API authorization is inferred from the chat subscription. No current pricing is assumed when its owning page cannot be accessed. A cost plan must state rate provenance and reserve worst-case request cost before submission. Failed/unknown-usage requests retain their full reservation until reconciled; there is no automatic retry or model fallback.

## Main study requirements

- Richer independently authored marketing cases, with several reasonable actions, a neutral shared capability catalog and multiple business objectives.
- Two context conditions analyzed separately: a verified complete reference and a fixed realistic imperfect context. Every recommendation method sees the same context within a condition.
- Deterministic scoring for source validity, current approved policy, access, prerequisites and budget. Sets of acceptable alternatives or partial preferences for strategic choice; never an arbitrary single gold action.
- Blinded practitioner assessment for specificity, expected usefulness, missing-information recognition and required corrections. Record annotator count, expertise, rubric, disagreement and disclosure. LLM judges are a separate disclosed signal, never relabeled human assessment.
- Coverage/abstention and inappropriate recommendations alongside quality. Report raw proposals, post-validation outputs and correction/latency/resource costs.
- Paired company-level intervals; model-by-method interaction; equal tuning effort; retained failures and prompts; model version, date, sampling controls, tokens and bill methodology.

## Distinct contribution and publication

Paper B explains recommendation reasoning and checks **conditional on supplied context**. It must not attribute gains to a better memory. Paper A explains context provision. Shared data and traces are disclosed and cross-referenced, not republished as independent confirmations. A joint factorial study can later test their interaction.

There are currently no Claude/GPT outcomes in this project, no independent human strategic-usefulness ratings and no revenue outcomes. The paper remains pending until actual evidence exists. Code and a protocol can be released with those statuses explicit; a fabricated empirical manuscript cannot.
