# Real GBrain component adapter

Upstream: https://github.com/garrytan/gbrain, pinned revision
`531b3b1ab66c88f192abb51338028c44b80fbf21` (MIT; Garry Tan, 2026).
Bun 1.4.0; upstream lockfile installed with `--frozen-lockfile --ignore-scripts --production`.
No global agent/MCP configuration, enrichment daemon, sharing or API keys are installed.

`search.ts` calls the real upstream PGLite engine, revision-bound page/chunk
installation and `hybridSearch`. It supplies the same **real recorded Qwen3
embeddings** as the research adapters through upstream's injectable vector seam.
It verifies that the semantic arm actually ran and refuses a silent lexical-only
fallback. This is not mocked retrieval. It is also not a full GBrain product
evaluation: graph extraction, paid reranking/expansion, synthesis, raw-document
ingestion, native permission enforcement and hosted behavior are outside scope.

Every method receives the same current permitted verified events. The shared
filter and shared embeddings isolate evidence selection; their correctness cannot
be credited to either memory product. Page titles carry the full fact text and
one chunk corresponds to one fact, giving the upstream keyword/title arms usable
content. No gold labels, accepted action IDs or future records enter this adapter.
The exact input and output are preserved for every attempted query.

Read `protocol-v0.1.md` before running. A successful smoke call is integration
evidence, not a market ranking. Main claims require a broader prospective study.

## Fresh native execution

The following reproduces the recorded Linux x86-64 setup. Network access is
needed to install public upstream code and dependencies. Bun's platform package
does not install agent configuration or use paid APIs. The source revision check
in `run.py` rejects a different or modified upstream checkout.

```sh
git clone --filter=blob:none --no-checkout https://github.com/garrytan/gbrain .cache/upstream/gbrain
git -C .cache/upstream/gbrain checkout --detach 531b3b1ab66c88f192abb51338028c44b80fbf21
npm install --prefix .cache/gbrain-runtime --ignore-scripts --no-audit --no-fund @oven/bun-linux-x64@1.4.0
```

From the research root, install GBrain's pinned dependencies without lifecycle
scripts. Both paths must be absolute because Bun changes the working directory:

```sh
RESEARCH_BUN="$(pwd)/.cache/gbrain-runtime/node_modules/@oven/bun-linux-x64/bin/bun"
RESEARCH_GBRAIN="$(pwd)/.cache/upstream/gbrain"
BUN_INSTALL_CACHE_DIR="$(pwd)/.cache/bun-cache" "$RESEARCH_BUN" install --cwd "$RESEARCH_GBRAIN" --frozen-lockfile --ignore-scripts --production
```

Start the pinned local reader/tokenizer described in the release README in a
separate terminal. This comparison makes no reader generation calls. Use the
included, actual main-study embedding cache; it contains the required vectors.
The matching embedder can be started as documented if reproducing embeddings,
but the saved-vector native experiment requires no new embedding requests.

```sh
python benchmarks/gbrain/run.py --data data/study/main-v1 \
  --output new-gbrain-run --upstream "$RESEARCH_GBRAIN" --bun "$RESEARCH_BUN" \
  --cache experiments/main/primary/embeddings.jsonl --token-cap 1024
python benchmarks/gbrain/analyze.py --run new-gbrain-run --data data/study/main-v1 \
  --cache experiments/main/primary/embeddings.jsonl --output new-gbrain-analysis
```

Use new output directories. All planned cases, including errors, remain in the
ledger. An all-error integration attempt is not successful retrieval evidence.
Saved-output analysis, including all three context budgets, needs neither Bun
nor any running service; see the offline command in the release README.
