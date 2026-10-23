#!/usr/bin/env bash
set -euo pipefail
research_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$research_root"
case "${1:-}" in
  reader)
    exec .cache/inference/build-avx512/bin/llama-server \
      --model .cache/models/Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf \
      --alias qwen3-30b-a3b-instruct-2507-q4_k_m --host 127.0.0.1 --port 8080 \
      --threads 4 --threads-batch 4 --ctx-size 16384 --parallel 1 \
      --no-cache-prompt --metrics
    ;;
  embedding)
    exec .cache/inference/build/bin/llama-server \
      --model .cache/models/Qwen3-Embedding-0.6B-Q8_0.gguf \
      --alias qwen3-embedding-0.6b-q8_0 --host 127.0.0.1 --port 8081 \
      --threads 4 --threads-batch 4 --ctx-size 4096 --batch-size 2048 \
      --ubatch-size 2048 --parallel 1 --embedding --pooling last
    ;;
  *) echo 'Usage: bash scripts/start_research_model.sh reader|embedding' >&2; exit 2 ;;
esac
