#!/usr/bin/env python3
"""Fetch only the hash-verified upstream development corpus, not multi-GB reports."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
PIN='6999ebc9da0ac784ac05995b586d22293544e924'
BASE=f'https://raw.githubusercontent.com/garrytan/gbrain-evals/{PIN}/'
PREFIX='eval/data/messy-company-v1/'
DEST=ROOT/'data/external/messy-company-v1'

def get(path):
    request=urllib.request.Request(BASE+path,headers={'User-Agent':'MarketingMemoryResearch/0.2'})
    with urllib.request.urlopen(request,timeout=30) as r:
        body=r.read(2*1024*1024+1)
    if len(body)>2*1024*1024:raise ValueError('unexpected large file')
    return body

def main():
    DEST.mkdir(parents=True,exist_ok=False)
    manifest_bytes=get(PREFIX+'MANIFEST.json');manifest=json.loads(manifest_bytes)
    (DEST/'UPSTREAM_MANIFEST.json').write_bytes(manifest_bytes)
    selected=[r for r in manifest['files'] if r['path'].startswith('corpus/dev/')
              or r['path']=='labels/agent-tasks/dev.jsonl']
    def fetch(row):
        path=PurePosixPath(row['path'])
        if path.is_absolute() or '..' in path.parts:raise ValueError('unsafe upstream path')
        raw=get(PREFIX+str(path));digest=hashlib.sha256(raw).hexdigest()
        if digest!=row['sha256'] or len(raw)!=row['bytes']:raise ValueError('upstream hash/size mismatch')
        out=DEST/str(path);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
        return dict(path=str(path),sha256=digest,bytes=len(raw),url=BASE+PREFIX+str(path))
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,selected))
    for path,out in [('LICENSE','LICENSE-UPSTREAM'),(PREFIX+'README.md','UPSTREAM_README.md'),
                     (PREFIX+'SCORING.md','UPSTREAM_SCORING.md'),('eval/CREDITS.md','UPSTREAM_CREDITS.md')]:
        raw=get(path);(DEST/out).write_bytes(raw)
        rows.append(dict(path=out,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),url=BASE+path))
    receipt=dict(fetched_at=datetime.now(timezone.utc).isoformat(),upstream_revision=PIN,
        upstream_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),files=rows,
        split='development only; no held-out corpus or answer rows downloaded',
        provenance='External project-authored fictional dataset; AI-written prose and cross-model checks; not human domain validation.',
        license='Upstream MIT. Original attribution retained separately from our original CC BY material.')
    (DEST/'FETCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'upstream_revision':PIN}))

if __name__=='__main__':main()
