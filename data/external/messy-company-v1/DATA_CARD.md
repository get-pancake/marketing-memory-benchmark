# External development corpus — messy-company-v1

Source: `garrytan/gbrain-evals`, revision
`6999ebc9da0ac784ac05995b586d22293544e924`.
All downloaded original bytes are checked against the upstream manifest. Exact
URLs, file hashes and sizes: `FETCH_RECEIPT.json`. License: `LICENSE-UPSTREAM`
(MIT); retain upstream credits. This is third-party material, not covered by our
original-data CC BY declaration.

Only the development corpus and development `agent-tasks` labels were fetched:
118 Markdown pages and 22 questions. The held-out pages and answer rows were not
downloaded. The complete upstream manifest is retained for provenance, but its
presence is not a claim that every referenced file is locally available.

The setting is one fictional B2B software company and its customer accounts,
not a representative sample of independent companies or a customer dataset.
Pages are externally project-authored with AI-generated prose and cross-model
checking, as described by the upstream authors. This is neither human expert
annotation nor independent empirical proof of marketing usefulness.

`labels/` includes answers, accepted variants, evidence and traps and MUST stay
outside adapter inputs. A retrieval adapter may receive only the question text
and the relevant source corpus/permission view. Current and historical records,
contract changes and ambiguity must not be pre-resolved using gold labels.

The prospective study must inspect whether `evidence_slugs` denotes all required
support or a larger relevant set; label-set recall alone is not answerability.
This fetch is dataset/provenance preparation, not a completed raw-ingestion
experiment or a newly hidden evaluation set.
