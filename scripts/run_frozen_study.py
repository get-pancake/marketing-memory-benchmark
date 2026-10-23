#!/usr/bin/env python3
"""Run both frozen blocks serially; explicit recovery never repeats completed calls."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from study.run import source_hashes


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args()
    output=a.output_root if a.output_root.is_absolute() else ROOT/a.output_root
    if a.resume:
        if not output.is_dir():raise SystemExit('Resume root does not exist')
    else:output.mkdir(parents=True,exist_ok=False)
    for cap,folder in [(1024,'primary'),(1536,'sensitivity')]:
        freeze_path=ROOT/f'experiments/freeze-{cap}.json';freeze=json.loads(freeze_path.read_text())
        if freeze['source_sha256']!=source_hashes():raise SystemExit('Frozen source changed')
        target=a.output_root/folder
        physical=output/folder
        if a.resume and (physical/'manifest.json').exists():
            saved=json.loads((physical/'manifest.json').read_text())
            if saved['freeze']!=freeze:raise SystemExit('Saved freeze differs')
            if saved['complete']:
                print(f'Skipping already completed {folder}; no inference repeated.',flush=True);continue
        command=[sys.executable,'-m','study.run','--data','data/study/main-v1',
            '--output',str(target),'--model-config','experiments/qwen3-moe-study.json',
            '--runtime-manifest','experiments/qwen3-moe-runtime.json',
            '--embedding-cache',str(a.output_root/'primary/embeddings.jsonl'),
            '--methods',*freeze['methods'],'--token-cap',str(cap),'--order-seed',str(freeze['order_seed']),
            '--freeze',str(freeze_path),'--reuse-identical']
        if physical.exists():command.append('--resume')
        subprocess.run(command,cwd=ROOT,check=True)


if __name__=='__main__':main()
