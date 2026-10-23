#!/usr/bin/env python3
"""Describe saved errors without changing scores, denominators or inference."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


POSITIVE = [
    'supported_recommendation', 'execution_or_output_failure',
    'no_complete_witness_selected', 'invalid_output_with_complete_witness',
    'withheld_with_complete_witness', 'inapplicable_choice_with_complete_witness',
    'invalid_support_with_complete_witness',
]
NEGATIVE = [
    'correct_withhold', 'execution_or_output_failure',
    'invalid_output', 'unsupported_recommendation',
]
CONTRASTS = [('typed', 'prompt_hybrid'), ('typed', 'facet_hybrid'),
             ('prompt_hybrid', 'generic_hybrid'), ('typed', 'typed_history'),
             ('full_context', 'typed')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def category(row):
    if row['decision_correct']:
        return 'supported_recommendation' if row['positive'] else 'correct_withhold'
    if row['status'] != 'completed':
        return 'execution_or_output_failure'
    if row['positive']:
        if not row['support_available']:
            return 'no_complete_witness_selected'
        if not row['schema_valid']:
            return 'invalid_output_with_complete_witness'
        if row['inappropriate_abstention']:
            return 'withheld_with_complete_witness'
        if not row['choice_correct']:
            return 'inapplicable_choice_with_complete_witness'
        return 'invalid_support_with_complete_witness'
    if not row['schema_valid']:
        return 'invalid_output'
    if row['recommended']:
        return 'unsupported_recommendation'
    raise ValueError('Unclassified completed negative decision; inspect scorer semantics')


def localize(folder):
    summary = json.loads((folder / 'summary.json').read_text())
    if not summary['source_run_complete']:
        raise ValueError('Only complete runs can enter this diagnostic')
    raw = (folder / 'per-attempt.jsonl').read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    if len(rows) != summary['planned_attempts']:
        raise ValueError('Planned denominator differs from saved rows')
    methods = {}
    indexed = {}
    for method, stats in summary['methods'].items():
        selected = sorted((r for r in rows if r['method'] == method),
                          key=lambda r: (r['case_id'], r['attempt_id']))
        indexed[method] = {r['case_id']: r for r in selected}
        if len(selected) != stats['planned'] or len(indexed[method]) != len(selected):
            raise ValueError('Missing or repeated method/case pair')
        positive = {key: 0 for key in POSITIVE}
        negative = {key: 0 for key in NEGATIVE}
        examples = {}
        availability = {f'available_{a}_correct_{c}': 0 for a in [0, 1] for c in [0, 1]}
        for row in selected:
            key = category(row)
            counts = positive if row['positive'] else negative
            counts[key] += 1
            group = ('positive/' if row['positive'] else 'negative/') + key
            examples.setdefault(group, {k: row[k] for k in
                ['case_id', 'attempt_id', 'world', 'condition', 'status', 'violations']})
            if row['positive']:
                a, c = int(row['support_available']), int(row['decision_correct'])
                availability[f'available_{a}_correct_{c}'] += 1
                if c and not a:
                    raise ValueError('Supported positive decision without an available witness')
        if sum(positive.values()) != stats['positive_cases'] or sum(negative.values()) != stats['negative_cases']:
            raise ValueError('Category totals differ from fixed denominators')
        if positive['supported_recommendation'] + negative['correct_withhold'] != round(stats['primary'] * stats['planned']):
            raise ValueError('Diagnostic changed primary successes')
        methods[method] = dict(positive=positive, negative=negative,
            positive_availability_by_correctness=availability,
            first_lexicographic_case_per_category=examples)
    comparisons = {}
    for left, right in CONTRASTS:
        if left not in indexed or right not in indexed:
            continue
        if indexed[left].keys() != indexed[right].keys():
            raise ValueError('Unpaired comparison')
        counts = Counter()
        disagreements = []
        for cid in sorted(indexed[left]):
            a, b = indexed[left][cid], indexed[right][cid]
            label = ('both_correct' if a['decision_correct'] and b['decision_correct'] else
                     'left_only' if a['decision_correct'] else
                     'right_only' if b['decision_correct'] else 'both_wrong')
            counts[label] += 1
            if label in ['left_only', 'right_only']:
                disagreements.append(dict(case_id=cid, world=a['world'], condition=a['condition'],
                    positive=a['positive'], outcome=label, left_category=category(a),
                    right_category=category(b), left_attempt_id=a['attempt_id'], right_attempt_id=b['attempt_id']))
        key = left + ' minus ' + right
        difference = (counts['left_only'] - counts['right_only']) / len(indexed[left])
        if abs(difference - summary['paired_contrasts'][key]['mean']) > 1e-12:
            raise ValueError('Case counts disagree with balanced paired-world effect')
        comparisons[key] = dict(counts={k: counts[k] for k in
            ['both_correct', 'left_only', 'right_only', 'both_wrong']}, disagreements=disagreements)
    normalized = {k: v for k, v in summary.items() if k not in ['analyzed_at', 'run', 'dataset']}
    return dict(schema='error-localization-v1', created_at=datetime.now(timezone.utc).isoformat(),
        source_per_attempt_sha256=sha(raw),
        source_summary_semantic_sha256=sha(json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()),
        script_sha256=sha(Path(__file__).read_bytes()), methods=methods, comparisons=comparisons,
        interpretation='Descriptive post-freeze, pre-results diagnostic. Categories preserve the original score and all planned denominators; they are not causal mediation estimates or new hypothesis tests. Failure precedes missing support in the exclusive category order. Examples are the first case ID per category, not independently representative selections. All paired disagreements are retained.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analysis', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = localize(a.analysis)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'output': str(a.output), 'methods': len(result['methods']),
                      'source_per_attempt_sha256': result['source_per_attempt_sha256']}))
