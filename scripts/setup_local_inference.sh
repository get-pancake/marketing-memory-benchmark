#!/usr/bin/env bash
set -euo pipefail
research_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$research_root"
uv --cache-dir .cache/uv venv --allow-existing .venv
uv --cache-dir .cache/uv pip install --python .venv/bin/python cmake==3.31.6
python3 - <<'PY'
import hashlib
from pathlib import Path
import tarfile
import urllib.request

revision = 'a37cc46104eb50900d5ab4a9ba02a0abdac039db'
expected = '784ada1e55d180e1ba26dbe37b881232bf259fd5b866a0ac28f8d2f9b08d3c1d'
root = Path('.cache/inference')
root.mkdir(parents=True, exist_ok=True)
archive = root / f'llama.cpp-{revision}.tar.gz'
if not archive.exists():
    url = f'https://codeload.github.com/ggml-org/llama.cpp/tar.gz/{revision}'
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = response.read(64 * 1024 * 1024 + 1)
    if len(payload) > 64 * 1024 * 1024 or hashlib.sha256(payload).hexdigest() != expected:
        raise SystemExit('Downloaded source archive failed integrity check')
    archive.write_bytes(payload)
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
    raise SystemExit('Cached source archive failed integrity check')
source = root / f'llama.cpp-{revision}'
with tarfile.open(archive) as contents:
    if not source.exists():
        contents.extractall(root, filter='data')
    for member in contents.getmembers():
        if member.isfile():
            target = root / member.name
            if not target.resolve().is_relative_to(root.resolve()) or target.is_symlink():
                raise SystemExit('Unsafe source member')
            if not target.exists() or hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(contents.extractfile(member).read()).digest():
                raise SystemExit('Source tree differs from pinned archive; inspect before changing it')
PY
# Prevent the source archive's build metadata from inheriting the research
# repository's Git identity. The exact upstream source revision is pinned above.
GIT_CEILING_DIRECTORIES="$research_root/.cache/inference" .venv/bin/cmake \
  -S .cache/inference/llama.cpp-a37cc46104eb50900d5ab4a9ba02a0abdac039db \
  -B .cache/inference/build -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=OFF -DGGML_AVX2=ON -DGGML_AVX512=OFF \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF \
  -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF
.venv/bin/cmake --build .cache/inference/build --target llama-server -j 3
.cache/inference/build/bin/llama-server --version
# This prepares the CPU binary only. No model weights, inference or server
# process are created. Verify a model's license, revision and hash separately.
