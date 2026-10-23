#!/usr/bin/env python3
"""Check input-budget feasibility with complete witnesses; no reader generation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from study.contract import applicable, canonical, visible
from study.retrieval import messages, post


def sha(data):
    return hashlib.sha256(data).hexdigest()


def witness_inputs(data):
    worlds = {w['id']: w for w in data['worlds']}
    rows = []
    for case in data['queries']:
        query = case['query']
        world = worlds[query['world']]
        events = visible(world['events'], query)
        truth = applicable(events, query, world['catalog'])
        if not truth:
            continue
        tid = sorted(truth)[0]
        ids = {sorted(group)[0] for group in truth[tid]}
        witness = [e for e in events if e['id'] in ids]
        for method in ['generic_hybrid', 'prompt_hybrid']:
            msg = messages(query, world['catalog'], witness, method)
            rows.append(dict(case_id=case['id'], world=query['world'], method=method,
                witness_template=tid, witness_ids=sorted(ids), messages=msg,
                messages_sha256=sha(canonical(msg).encode())))
    return rows


def summarize(rows):
    result = {}
    for method in ['generic_hybrid', 'prompt_hybrid']:
        values = [r['token_count'] for r in rows if r['method'] == method]
        result[method] = dict(positive_queries=len(values), minimum=min(values), maximum=max(values),
                             fit_1024=sum(v <= 1024 for v in values), fit_1536=sum(v <= 1536 for v in values))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=ROOT / 'data/study/main-v1')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path, help='New receipt; uses local chat-template/tokenizer metadata endpoints only.')
    mode.add_argument('--verify-saved', type=Path, help='Offline consistency check of saved messages, token arrays and summaries.')
    a = p.parse_args()
    data_path = a.data / 'inputs.json'
    data = json.loads(data_path.read_text())
    expected = witness_inputs(data)
    if a.verify_saved:
        saved = json.loads(a.verify_saved.read_text())
        if saved['inputs_sha256'] != sha(data_path.read_bytes()) or len(expected) != len(saved['records']):
            raise ValueError('Input data or record count differs')
        for want, row in zip(expected, saved['records']):
            if any(row[k] != v for k, v in want.items()):
                raise ValueError('Witness/message differs')
            if row['token_count'] != len(row['tokenize_response']['tokens']):
                raise ValueError('Token count differs from retained response')
            if row['rendered_prompt_sha256'] != sha(row['apply_template_response']['prompt'].encode()):
                raise ValueError('Rendered prompt hash differs')
        if summarize(saved['records']) != saved['summary']:
            raise ValueError('Summary differs')
        print(json.dumps({'verified': True, 'reader_generation_calls': 0, 'summary': saved['summary'],
                          'limit': 'Offline receipt consistency; fresh tokenization requires the pinned runtime.'}))
        return
    if a.output.exists():
        raise ValueError('Output exists; preserve the prior receipt')
    for row in expected:
        applied = post('http://127.0.0.1:8080/apply-template', {'messages': row['messages']})
        tokenized = post('http://127.0.0.1:8080/tokenize', {'content': applied['prompt'], 'add_special': False})
        row.update(apply_template_response=applied, tokenize_response=tokenized,
                   rendered_prompt_sha256=sha(applied['prompt'].encode()), token_count=len(tokenized['tokens']))
    result = dict(created_at=datetime.now(timezone.utc).isoformat(),
        kind='input_only_witness_capacity_diagnostic', reader_generation_calls=0,
        reads_experimental_outcomes=False, inputs_sha256=sha(data_path.read_bytes()),
        script_sha256=sha(Path(__file__).read_bytes()),
        runtime=json.loads((ROOT / 'experiments/qwen3-moe-runtime.json').read_text()),
        records=expected, summary=summarize(expected),
        limitation='One deterministic complete minimal-slot witness per positive query. Not a new retrieval method or a proof of token optimality. No run ledgers or labels are read; no inference outcome informs the diagnostic. Chat-template/tokenizer metadata requests are not reader-generation requests.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'reader_generation_calls': 0, 'summary': result['summary'], 'output': str(a.output)}))


if __name__ == '__main__':
    main()
