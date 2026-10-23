#!/usr/bin/env python3
"""Audit/analyze both completed frozen blocks and render figures; never infer."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from study.run import source_hashes


def now():
    return datetime.now(timezone.utc).isoformat()


def ready():
    for block in ['primary', 'sensitivity']:
        path = ROOT / 'experiments/main' / block / 'manifest.json'
        if not path.exists() or not json.loads(path.read_text())['complete']:
            return False
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wait', action='store_true', help='Wait for both blocks without launching model calls.')
    a = p.parse_args()
    while not ready():
        if not a.wait:
            raise SystemExit('Both frozen main blocks must be complete before analysis.')
        time.sleep(30)
    for cap, block in [(1024, 'primary'), (1536, 'sensitivity')]:
        freeze = json.loads((ROOT / f'experiments/freeze-{cap}.json').read_text())
        run = json.loads((ROOT / 'experiments/main' / block / 'manifest.json').read_text())
        if freeze['source_sha256'] != source_hashes() or run['freeze'] != freeze:
            raise ValueError('Frozen source/configuration differs: ' + block)
    output = ROOT / 'analysis/main'
    output.mkdir(parents=True, exist_ok=False)
    receipt = dict(started_at=now(), complete=False, model_calls=0, commands=[],
                   scope='Analysis of saved actual outputs only, after both frozen blocks completed.')
    path = output / 'evidence-build.json'
    def save():
        path.write_text(json.dumps(receipt, indent=2) + '\n')
    def run(label, command):
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log = output / (label + '.log')
        log.write_text(result.stdout)
        receipt['commands'].append(dict(label=label, argv=command, exit_code=result.returncode,
                                         log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        save()
        if result.returncode:
            raise RuntimeError('Evidence build failed: ' + label)
        print(label + ': completed', flush=True)
    save()
    try:
        for block in ['primary', 'sensitivity']:
            run_path = 'experiments/main/' + block
            dest = 'analysis/main/' + block
            run('audit-' + block, [sys.executable, 'analysis/audit_run.py', '--run', run_path,
                                   '--data', 'data/study/main-v1', '--output', dest + '/provenance-audit.json'])
            run('analysis-' + block, [sys.executable, 'analysis/analyze_study.py', '--run', run_path,
                                      '--data', 'data/study/main-v1', '--output', dest])
            run('figures-' + block, [sys.executable, 'analysis/figures.py', '--analysis', dest + '/summary.json',
                                     '--output', 'paper/figures/' + block])
        run('sql-reference', [sys.executable, '-m', 'study.reference', '--data', 'data/study/main-v1',
                              '--output', 'experiments/main/sql-reference'])
        receipt['complete'] = True
    finally:
        receipt['finished_at'] = now()
        save()
    print(json.dumps({'complete': True, 'model_calls': 0, 'receipt': str(path)}))


if __name__ == '__main__':
    main()
