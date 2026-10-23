#!/usr/bin/env python3
"""Download a pinned Apache-2.0 CPU research model, checking its public LFS hash.

Weights are a local cache, not included in the public companion. No credentials
or paid API are used. HTTPS certificate verification remains enabled.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPO = "unsloth/Qwen3-4B-Instruct-2507-GGUF"
REVISION = "a06e946bb6b655725eafa393f4a9745d460374c9"
NAME = "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
SHA256 = "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597"
SIZE = 2497281120


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    global REPO, REVISION, NAME, SHA256, SIZE
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--embedding", action="store_true")
    choice.add_argument("--larger-model", action="store_true")
    choice.add_argument("--moe-model", action="store_true")
    args = parser.parse_args()
    if args.embedding:
        REPO = "Qwen/Qwen3-Embedding-0.6B-GGUF"
        REVISION = "370f27d7550e0def9b39c1f16d3fbaa13aa67728"
        NAME = "Qwen3-Embedding-0.6B-Q8_0.gguf"
        SHA256 = "06507c7b42688469c4e7298b0a1e16deff06caf291cf0a5b278c308249c3e439"
        SIZE = 639150592
    elif args.moe_model:
        REPO = "unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF"
        REVISION = "eea7b2be5805a5f151f8847ede8e5f9a9284bf77"
        NAME = "Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf"
        SHA256 = "6c997b8af17debdfb01d890214400ccbab00db6acc0ba8da5de1cc906c4774d0"
        SIZE = 18556686752
    elif args.larger_model:
        REPO = "unsloth/Qwen3.5-9B-GGUF"
        REVISION = "3885219b6810b007914f3a7950a8d1b469d598a5"
        NAME = "Qwen3.5-9B-Q4_K_M.gguf"
        SHA256 = "03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8"
        SIZE = 5680522464
    destination = ROOT / ".cache" / "models" / NAME
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    if destination.exists():
        if destination.stat().st_size != SIZE or digest(destination) != SHA256:
            raise ValueError("Existing model does not match the pinned artifact")
    else:
        partial = destination.with_suffix(".partial")
        url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{NAME}"
        with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as output:
            received = 0
            while block := response.read(8 * 1024 * 1024):
                received += len(block)
                if received > SIZE:
                    raise ValueError("Download exceeds declared model size")
                output.write(block)
        if partial.stat().st_size != SIZE or digest(partial) != SHA256:
            raise ValueError("Downloaded model does not match the public LFS hash")
        partial.rename(destination)
    print(json.dumps({"path": str(destination.relative_to(ROOT)), "sha256": SHA256,
                      "size": SIZE, "repository": REPO, "revision": REVISION,
                      "elapsed_seconds": time.monotonic() - started}))


if __name__ == "__main__":
    main()
