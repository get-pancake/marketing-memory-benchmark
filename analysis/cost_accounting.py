#!/usr/bin/env python3
"""Reconcile shared computation and method charges from completed run ledgers."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def origin_totals(origins):
    return {kind: dict(items=sum(r['kind'] == kind for r in origins.values()),
                       seconds=sum(r['seconds'] for r in origins.values() if r['kind'] == kind))
            for kind in ['event', 'query']}


def account(paths):
    blocks = {}; all_origins = {}; global_known_new_embedding_seconds = 0
    for path in paths:
        manifest = json.loads((path / 'manifest.json').read_text())
        if not manifest['complete']:
            raise ValueError('Only complete run ledgers can be accounted: ' + str(path))
        ledger = [json.loads(line) for line in (path / 'attempts.jsonl').read_text().splitlines()]
        issued = {r['attempt_id'] for r in ledger if r['status'] == 'model_call_started'}
        terminal = [r for r in ledger if r['status'] in ['completed', 'failed']]
        if len(terminal) != len(manifest['planned']) or len({r['attempt_id'] for r in terminal}) != len(terminal):
            raise ValueError('Missing or duplicate terminal attempts')
        grouped = defaultdict(list)
        for row in terminal:
            grouped[row['method']].append(row)
        methods = {}; block_origins = {}; known_new_embedding_seconds = 0
        for method, rows in sorted(grouped.items()):
            origins = {}; retrieval_seconds = 0; new_embedding_seconds = 0
            for row in rows:
                retrieval = row.get('retrieval', {})
                retrieval_seconds += retrieval.get('seconds', 0)
                for item in retrieval.get('embedding_receipts', []):
                    origin = dict(kind=item['kind'], seconds=item.get('origin_seconds', item['seconds']))
                    for cache in [origins, block_origins, all_origins]:
                        if item['key'] in cache and cache[item['key']] != origin:
                            raise ValueError('Embedding origin changes between receipts')
                        cache[item['key']] = origin
                    if not item['cache_hit']:
                        new_embedding_seconds += item['seconds']
            overhead = retrieval_seconds - new_embedding_seconds
            if overhead < -1e-6:
                raise ValueError('Nested embedding time exceeds retrieval elapsed time')
            logical_generation = sum(r.get('generation_seconds') or 0 for r in rows)
            origin_seconds = sum(r['seconds'] for r in origins.values())
            methods[method] = dict(planned=len(rows),
                physical_calls=sum(r['attempt_id'] in issued for r in rows),
                reused_requests=sum(bool(r.get('model_request_reused')) for r in rows),
                charged_generation_seconds=logical_generation,
                observed_retrieval_seconds=retrieval_seconds,
                known_new_embedding_seconds_inside_retrieval=new_embedding_seconds,
                selection_and_tokenization_seconds_excluding_new_embeddings=max(0, overhead),
                unique_associated_embedding_origins=origin_totals(origins),
                charged_component_estimate_seconds=logical_generation + max(0, overhead) + origin_seconds,
                terminal_attempts_without_retrieval_receipt=sum('retrieval' not in r for r in rows),
                issued_calls_without_usage=sum(r['attempt_id'] in issued and 'usage' not in r for r in rows))
            known_new_embedding_seconds += new_embedding_seconds
        wall = (datetime.fromisoformat(manifest['finished_at']) - datetime.fromisoformat(manifest['started_at'])).total_seconds()
        physical_generation = sum(r.get('physical_generation_seconds', r.get('generation_seconds')) or 0 for r in terminal)
        block = dict(path=str(path), manifest_sha256=digest(path / 'manifest.json'),
            ledger_sha256=digest(path / 'attempts.jsonl'), wall_seconds=wall,
            planned=len(manifest['planned']), physical_calls=len(issued),
            reused_requests=sum(bool(r.get('model_request_reused')) for r in terminal),
            known_physical_generation_seconds=physical_generation,
            observed_retrieval_seconds=sum(s['observed_retrieval_seconds'] for s in methods.values()),
            known_new_embedding_seconds_inside_retrieval=known_new_embedding_seconds,
            unique_associated_embedding_origins=origin_totals(block_origins), methods=methods)
        if path.name in blocks:
            raise ValueError('Block names must differ')
        blocks[path.name] = block
        global_known_new_embedding_seconds += known_new_embedding_seconds
    return dict(schema='saved-computation-accounting-v1', blocks=blocks,
        unique_associated_embedding_origins_across_blocks=origin_totals(all_origins),
        known_new_embedding_seconds_inside_retrieval_across_blocks=global_known_new_embedding_seconds,
        known_physical_generation_seconds=sum(b['known_physical_generation_seconds'] for b in blocks.values()),
        summed_block_wall_seconds=sum(b['wall_seconds'] for b in blocks.values()),
        notes=[
            'All seconds are elapsed wall time, not summed CPU seconds or dollars. Shared-host timings are descriptive.',
            'Embedding work is nested inside observed retrieval time: never add it again to measured retrieval totals.',
            'Associated origins are deduplicated across both blocks; a warm sensitivity cache does not erase index work.',
            'Method component estimates charge each associated embedding origin once plus non-embedding selection/tokenization overhead and each logical generation origin. They are estimates from shared execution, not measured standalone cold-start deployments.',
            'Exact generation reuse charges the observed origin to each logical method comparison while physical totals count each request once. Unknown usage remains unknown.',
            'Training, natural-language extraction, human curation, model download/build, hardware rental and energy are outside these timed query components. No amortized commercial lifecycle-cost advantage is established.',
        ])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError('Output exists; preserve the previous accounting')
    result = account(a.runs)
    result.update(created_at=datetime.now(timezone.utc).isoformat(), script_sha256=digest(Path(__file__)))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(output=str(a.output), blocks=list(result['blocks']), reader_generation_calls=0)))


if __name__ == '__main__':
    main()
