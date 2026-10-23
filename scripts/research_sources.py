#!/usr/bin/env python3
"""Retrieve public primary sources with dated, hashed provenance; never execute them.

Downloaded materials are an ignored reading cache, not redistributable artifacts.
Example: python scripts/research_sources.py https://arxiv.org/abs/2508.11120
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "literature"
LOG = ROOT / "literature" / "retrievals.jsonl"
LIMIT = 32 * 1024 * 1024


def retrieve(url: str) -> dict:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only public HTTPS URLs without embedded credentials are accepted")
    record = {"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
              "purpose": "primary-source review", "redistribution_rights": "not established"}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "PancakeResearch/0.1"})
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read(LIMIT + 1)
            if len(content) > LIMIT:
                raise ValueError("Source exceeds the 32 MiB reading-cache limit")
            media_type = response.headers.get_content_type()
            suffix = ".pdf" if media_type == "application/pdf" or content.startswith(b"%PDF") else ".txt"
            path = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:20] + suffix)
            CACHE.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            record.update(status="retrieved", http_status=response.status,
                          final_url=response.url, media_type=media_type, bytes=len(content),
                          sha256=hashlib.sha256(content).hexdigest(), path=str(path.relative_to(ROOT)))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        record.update(status="unavailable", error_type=type(exc).__name__, error=str(exc))
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="+")
    args = parser.parse_args()
    failed = False
    for url in args.urls:
        record = retrieve(url)
        print(json.dumps(record, sort_keys=True), flush=True)
        failed |= record["status"] != "retrieved"
    raise SystemExit(int(failed))


if __name__ == "__main__":
    main()
