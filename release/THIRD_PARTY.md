# Attribution and dependency scope

The companion's research code is original implementation. BM25 and reciprocal-rank fusion are standard methods credited in the verified bibliography. The comparison design draws on the cited literature; no Hindsight, Graphiti, MemCompile, EnterpriseMem or other memory-system implementation is bundled as our own code. Private Pancake production code is not a dependency.

External runtime and weights are downloaded separately, never included in the ZIP:

| Component | Pin / provenance | License |
|---|---|---|
| llama.cpp | ggml-org/llama.cpp, a37cc46104eb50900d5ab4a9ba02a0abdac039db; source archive hash in setup script | MIT |
| Historical v1/v2 reader | Qwen3-30B-A3B-Instruct-2507; base 0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe; Unsloth GGUF eea7b2be5805a5f151f8847ede8e5f9a9284bf77 | Apache-2.0 |
| Historical v1/v2 embedding model | Official Qwen/Qwen3-Embedding-0.6B-GGUF, 370f27d7550e0def9b39c1f16d3fbaa13aa67728 | Apache-2.0 |
| Earlier 4B development reader | Qwen3-4B-Instruct-2507; Unsloth GGUF a06e946bb6b655725eafa393f4a9745d460374c9 | Apache-2.0 |
| Earlier 9B development reader | Qwen3.5-9B; base c202236235762e1c871ad0ccb60c8ee5ba337b9a; Unsloth GGUF 3885219b6810b007914f3a7950a8d1b469d598a5 | Apache-2.0 |

Official cards and generation-model LICENSE files were inspected. Exact weight filenames, byte counts and SHA-256 hashes are enforced by `scripts/download_research_model.py`. Quantized weights are credited to their base-model authors and the named quantization distributor. Earlier readers are needed only for fresh reproduction of their archived development runs; the archived v1/v2 experiment needs the MoE reader and embedding model. The current Opus/GPT challenge does not.

Python, CMake, the compiler/toolchain, NumPy, Matplotlib and their dependencies retain their respective licenses. The package contains a dependency lock and build instructions, not vendored copies of these libraries. System TeX compiles the manuscript; Pandoc converts the investor note's Markdown to LaTeX. Their observed versions are recorded in the PDF build receipts. Poppler's `pdftotext`/`pdfinfo` support reproduction checks. Hardware and compiler differences may affect fresh inference, latency and binary output.

Cited papers, third-party PDFs, author repository source caches and copied abstracts are not redistributed. Bibliographic facts, original critical summaries and stable source links provide attribution; inclusion does not imply endorsement or upstream-result reproduction. Original artifact data/documentation and code have separate CC BY 4.0 and MIT scope statements. No private repository history, credentials or customer data is licensed by this companion.

The optional literature scorer diagnostic downloads three hash-checked files from EnterpriseMem-Bench revision `819a8bc99db576a21828c2a8e6d273ae2ff023c4`: its MIT-licensed scoring module and a CC BY 4.0 ten-item finance question/answer subset. Upstream bytes remain a reading cache rather than bundled source. The original diagnostic wrapper, source attribution, brief answer probes and results are included; this is not a reproduction of the upstream memory-system comparison.

## Marketing-memory amendment

- GBrain source: `garrytan/gbrain` at `531b3b1ab66c88f192abb51338028c44b80fbf21`, MIT, copyright 2026 Garry Tan. The source is installed separately and is not bundled. Our component adapter calls its engine, projection and hybrid-search APIs; it does not copy the product. Bun 1.4.0 and GBrain's pinned dependency lock are external runtime requirements for fresh native execution. Original adapter code is MIT under this companion's code license.
- External `messy-company-v1` development corpus: `garrytan/gbrain-evals` at `6999ebc9da0ac784ac05995b586d22293544e924`. The included original source files retain upstream MIT and author credits in `data/external/messy-company-v1/LICENSE-UPSTREAM` and `UPSTREAM_CREDITS.md`. `FETCH_RECEIPT.json` records every included upstream file hash/URL. Only development source documents and development task labels are bundled; the held-out corpus/labels and multi-GB upstream run history are not.
- The integrated v3 artifact includes actual GPT-6.1 Sol and Claude Sonnet5.5 requests/responses and usage receipts, plus actual text-embedding-3-small vectors. API services and proprietary models are not redistributed or licensed by the companion. Fresh runs require independently supplied credentials and operator spending guards. Outputs are AI-generated research artifacts, not human labels or vendor endorsement. Official model/pricing URLs and check dates are recorded in providers.json.
- The Markdown wiki compiler is original code inspired by publicly discussed file-memory practice. The inspected community implementation Astro-Han/karpathy-llm-wiki (eafcc77001e496cc43499e4923b663aec722c813, MIT) is unofficial; no code or skill text is copied. Karpathy’s owning Gist could not be retrieved from this runtime; no unverified quotation or official-product claim is made.

## Opus challenge (v4)

The current main and external extension use actual `claude-opus-5-5`, with adaptive thinking/high effort. The other main reader is `gpt-6.1-sol`, medium reasoning. Saved usage, exact model IDs, prompts and returned response IDs are included. Current OpenAI/Anthropic services are separately accessed under their own terms; no proprietary model or API entitlement is redistributed. Actual `text-embedding-3-small` vectors are saved as research outputs in lossless shards, along with raw generation/embedding responses. They are not model weights. Prices and availability have dated official-source evidence.

The main challenge is original structured synthetic data. Both generic and task-aligned selectors share clean temporal/access metadata, native GBrain ranking, a public catalog and a common packer. Native telemetry explicitly records that the composite query had no lexical matches in this configuration; this is not the full GBrain agent or a market-product ranking. The stronger generic query-word selector exactly matches the specialized packets. The external Opus extension reuses MIT-licensed upstream development documents and earlier query-blind wiki compilations; it is separate from the 120-world main sample.

Additional methodological reading of τ-bench, AppWorld and τ²-bench is documented at selected-methods/evaluation depth. Only verified bibliographic metadata and original critical notes are distributed, not third-party paper PDFs or copied benchmark code/data.
