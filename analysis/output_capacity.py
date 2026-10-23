#!/usr/bin/env python3
"""Audit response-budget capacity from public contracts; no reader generation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from study.contract import applicable, score, slot_name, visible
from study.retrieval import aliases, materialize_output, post


def sha(data):
    return hashlib.sha256(data).hexdigest()


def witnesses(data):
    worlds = {w['id']: w for w in data['worlds']}
    records = []
    for case in data['queries']:
        q = case['query']; w = worlds[q['world']]
        events = [e for e in visible(w['events'], q) if e['entity'] in ['seller', q['account']]]
        truth = applicable(events, q, w['catalog'])
        names = {v: k for k, v in aliases(events).items()}
        support = {}
        for template in w['catalog']:
            for requirement in template['requirements']:
                slot = slot_name(requirement)
                if slot in support:
                    continue
                entity = q['account'] if requirement['entity'] == '$account' else requirement['entity']
                found = [e for e in events if (e['entity'], e['key'], e['authority']) ==
                         (entity, requirement['key'], requirement['authority'])]
                support[slot] = names[min(e['id'] for e in found)] if found and len({e['value'] for e in found}) == 1 else None
        raw = dict(support=support, status='recommend' if truth else 'request_evidence',
                   template=sorted(truth)[0] if truth else None,
                   missing=[] if truth else ['Contract prerequisites not satisfied.'])
        output, bindings = materialize_output(raw, events, w['catalog'])
        checked = score(output, w['events'], events, q, w['catalog'], list(truth), bindings)
        if not checked['decision_correct']:
            raise ValueError('Constructed witness violates the declared contract: ' + case['id'])
        for label, options in [('compact', dict(separators=(',', ':'))), ('indented', dict(indent=2))]:
            content = json.dumps(raw, ensure_ascii=False, **options)
            records.append(dict(case_id=case['id'], positive=bool(truth), format=label,
                raw_response=raw, content=content, content_sha256=sha(content.encode()),
                decision_correct=True))
    return records


def summarize(records):
    result = {}
    for form in ['compact', 'indented']:
        rows = [r for r in records if r['format'] == form]
        counts = [r['tokens_including_one_end_token'] for r in rows]
        result[form] = dict(queries=len(rows), positive_queries=sum(r['positive'] for r in rows),
            minimum=min(counts), maximum=max(counts), fit_280=sum(n <= 280 for n in counts))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=ROOT / 'data/study/main-v1')
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--output', type=Path)
    modes.add_argument('--verify-saved', type=Path)
    a = p.parse_args()
    data_path = a.data / 'inputs.json'
    expected = witnesses(json.loads(data_path.read_text()))
    if a.verify_saved:
        saved = json.loads(a.verify_saved.read_text())
        if saved['inputs_sha256'] != sha(data_path.read_bytes()) or len(expected) != len(saved['records']):
            raise ValueError('Input hash or record count differs')
        for want, row in zip(expected, saved['records']):
            if any(row[k] != v for k, v in want.items()):
                raise ValueError('Witness differs')
            if row['tokens_including_one_end_token'] != len(row['tokenize_response']['tokens']) + 1:
                raise ValueError('Token count differs')
        if saved['summary'] != summarize(saved['records']):
            raise ValueError('Summary differs')
        print(json.dumps(dict(verified=True, reader_generation_calls=0, summary=saved['summary'])))
        return
    if a.output.exists():
        raise ValueError('Output exists; preserve the prior receipt')
    for row in expected:
        tokenized = post('http://127.0.0.1:8080/tokenize', {'content': row['content'], 'add_special': False})
        row.update(tokenize_response=tokenized, tokens_including_one_end_token=len(tokenized['tokens']) + 1)
    result = dict(created_at=datetime.now(timezone.utc).isoformat(), reader_generation_calls=0,
        kind='output_only_contract_witness_capacity_diagnostic', reads_experimental_outcomes=False,
        inputs_sha256=sha(data_path.read_bytes()), script_sha256=sha(Path(__file__).read_bytes()),
        runtime=json.loads((ROOT / 'experiments/qwen3-moe-runtime.json').read_text()),
        records=expected, summary=summarize(expected),
        limitation='One rule-constructed correct decision per query, serialized compactly and with two-space indentation over the complete current view. Tokenizer receipts plus one end token establish representational capacity, not model success, token-optimal encoding, free-text explanation quality or behavior of every possible serialization. No labels or run ledger read; no reader-generation calls.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(reader_generation_calls=0, summary=result['summary'], output=str(a.output))))


if __name__ == '__main__':
    main()
