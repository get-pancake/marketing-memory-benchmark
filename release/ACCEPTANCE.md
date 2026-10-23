# Public companion v1.0.0 — acceptance record

**Domain-Specialized Company Memory for Grounded Marketing Recommendations**, by **Guillaume Marquis**. This record verifies the prepared public payload; it does not assert that a GitHub repository has already been created or that the paper has been submitted or peer reviewed.

## Report and evidence

- Current report: `paper/report.pdf`, 13 pages, SHA-256 `9a7f37a31a58b358384ec62fb6a1fb043d229408068c7d517f93f124f6eb5e84`. Eight vector figures and four tables; title and author match the PDF metadata.
- Investor note: `paper/investor-note.pdf`, two pages, SHA-256 `89307cb017382cb15c1815d9865bc9599d3c69b207f2e6ba3a1d6c4a2be51659`.
- `release/VISUAL_INSPECTION.json` covers both exact PDFs. The editorial title/author changes were inspected; the other 12 main pages render identically to the original v4 report. No final TeX layout warnings were observed.
- Main experiment: 120 original fictional companies, 360 multi-account cases, six executed contexts, two readers and 4,320 actual responses. Zero technical failures. Models: `gpt-6.1-sol` and `claude-opus-5-5` with their frozen settings.
- All requests, outputs, usage, pilot amendments, negative outcomes, independent reference checks and historical experiments remain available. No new model observations were added for public packaging.

On the 288 positive cases, general company context yields 47.8573% of the formal optimum for both readers; specialized context yields 88.4294% for GPT and 88.1884% for Opus. Paired gains are 40.5721 and 40.3312 percentage points, with company-bootstrap 95% intervals [36.7341, 44.4228] and [36.3435, 44.3227]. All 72 negative cases are safely withheld by every treatment. These are constructed, grounded policy-priority scores, not revenue or independent human preference.

The generic query-word control exactly matches the specialized inputs and adds no independent observations. Full current context performs better with a larger allowance; wider generic contexts close the retrieval gap. The external one-company development extension favors the general wiki, 22/22 versus 21/22. The native GBrain row is one search-component configuration, not a complete-product ranking. These boundaries remain prominent in the README and paper.

## Exact-payload reproduction

The final candidate was extracted into `/tmp/marketing-memory-public-clean2` outside the private research tree. A newly installed, hash-pinned Python 3.12 environment was used; the second metadata-only candidate reused that isolated environment. System TeX/BibTeX, Pandoc and Poppler are shared host dependencies. This is saved-output reproduction on the same host, not independent hardware or fresh model inference.

The final run passed from **2026-10-23T08:14:18.750518+00:00** to **2026-10-23T08:16:59.738550+00:00**: **47 commands, 25 checks, 93 tests, zero fresh provider calls**. Receipt: `release/reproduction-records/clean-reproduction.json`.

Verified core payload SHA-256:

`b9e6ab8a34c89963ff0712a42d853e83357eed575bfa0175d143f20fd15e8a5f`

The run verified every candidate file and reproduced the datasets, SQL/exhaustive reference labels, all context packets, all saved-response scores, company-clustered uncertainty, costs, failure analysis, embeddings, eight figures and both PDF text/layouts. It left all packaged evidence unchanged. The first passing public candidate is retained under `publication-candidate-attempt1/`; the only later core change clarified publication status. Earlier v4 and v3 receipts remain under their versioned paths.

Additional publication checks confirmed 27 local README links, headline percentages against saved analysis, valid CFF 1.2.0 citation metadata, valid read-only GitHub Actions configuration, and successful quick-start commands with Python site packages disabled. GitHub Actions has not yet run remotely. A pattern scan covered all candidate payload text and 28 PDFs, with no credential/private-pointer matches. The largest file is 29,591,363 bytes, below GitHub's 100 MiB per-file limit. See `public-payload-audit.json`; the final archive is independently checked before transfer.

## Licensing and publication boundary

Original code is MIT. Specified original research data, outputs and documentation are CC BY 4.0. External company documents retain upstream MIT and credits. Models/services are separately accessed. The public allowlist excludes private planning history, credentials, production source, customer records, model weights and third-party paper PDFs.

The working research repository remains private. The intended public destination is `get-pancake/marketing-memory-benchmark`; public release uses a fresh Git history. Its live visibility must be checked separately. No Hacker News/social post, arXiv submission or venue submission is part of this acceptance record.

`MANIFEST.json` hashes every included file. Reproduction records and this acceptance narrative are excluded only from the core digest to avoid circular references; their individual hashes remain in the manifest. Run `python scripts/reproduce_saved.py --output NEW_DIRECTORY` after the documented dependency installation to verify the saved evidence again.
