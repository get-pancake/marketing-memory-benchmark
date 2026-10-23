# Controlled GTM Play study

This package is an actual-model comparison over fictional verified events. The earlier `prototype/` remains a separate development artifact. Protocol: `papers/company-memory/protocol/pilot-v1.md`.

Correctness checks (no model calls):

```sh
python3 -m unittest study.test_contract study.test_ledger analysis.test_analysis -v
```

Local model runtime, licenses, pins and hashes are documented in `scripts/download_research_model.py`, `experiments/*runtime.json`, and the run manifests. Earlier development used a 4B and a 9B reader. The current reader candidate is Qwen3-30B-A3B-Instruct-2507 Q4_K_M (18.56 GB), with Qwen3-Embedding-0.6B Q8_0 (0.64 GB). Fresh inference requires the weights, approximately 32 GiB RAM and substantial CPU time; no paid API key is required. Consult saved state before starting a duplicate server or rerunning a completed experiment.

Prepare the pinned runtime with `bash scripts/setup_local_inference.sh`, then build its AVX512 variant using `worklog/avx512-build.md` on compatible hardware. Download the hash-checked weights with `python3 scripts/download_research_model.py --moe-model` and `python3 scripts/download_research_model.py --embedding`. Run `bash scripts/start_research_model.sh reader` and `bash scripts/start_research_model.sh embedding` in separate terminals. Both bind only to loopback. Other hardware/builds may change latency and numerical results.

Pilot Stage A (use a new output directory; do not overwrite a run):

```sh
python3 -m study.run --data data/study/pilot-v5 \
  --output experiments/pilot/your-new-competence-run \
  --model-config experiments/qwen3-moe-study.json \
  --runtime-manifest experiments/qwen3-moe-runtime.json \
  --methods full_context typed --conditions initial --token-cap 1024
```

The runner uses actual local inference, saves errors and raw outputs, and never falls back to a mock answer. The downstream dry-run intentionally uses deterministic fictional providers. These are different evidence categories. A main benchmark and final empirical release are not yet complete.

For an interrupted main run, repeat its exact command with `--resume` after restoring its pinned runtime. An exclusive lock rejects resumption while the original process is active. Completed/failed calls are never repeated. An issued attempt with no saved terminal response is closed as interrupted and counted as a failure, with unknown usage disclosed; only unstarted planned work resumes. A torn final write is preserved in `recovery/` before ledger repair. Source/data/settings must still match the saved run. Fault-injection tests exercise this behavior without contacting a model endpoint.
