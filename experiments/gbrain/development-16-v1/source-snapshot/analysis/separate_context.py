#!/usr/bin/env python3
"""Post-hoc context/reader decomposition of immutable v1 traces. No model calls."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from study.contract import applicable, visible, requirements
from analysis.analyze_study import paired_ci


def context_metrics(events, q, catalog, selected_ids):
    """Score evidence without consulting a generated recommendation."""
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError('duplicate selected source')
    current = visible(events, q)
    by_id = {e['id']: e for e in events}
    if any(i not in by_id for i in selected_ids):
        raise ValueError('unknown selected source')
    selected = [by_id[i] for i in selected_ids]
    current_ids = {e['id'] for e in current}
    current_selected = [e for e in selected if e['id'] in current_ids]
    truth = applicable(current, q, catalog)
    apparent = applicable(current_selected, q, catalog)
    needed = {k for t in catalog
              if t['objective'] == q['objective'] and t['units'] <= q['max_units']
              for k in requirements(t, q)}
    groups = defaultdict(set)
    for e in current:
        key = (e['entity'], e['key'], e['authority'])
        if key in needed:
            groups[key + (e['value'],)].add(e['id'])
    ids = set(selected_ids)
    covered = sum(bool(ids & values) for values in groups.values())
    complete = any(all(ids & values for values in alternatives)
                   for alternatives in truth.values())
    relevant = sum((e['entity'], e['key'], e['authority']) in needed
                   for e in current_selected)
    return dict(answerable=bool(truth), complete_positive_support=complete,
                required_current_value_groups=len(groups), covered_current_value_groups=covered,
                current_value_group_coverage=covered / len(groups) if groups else None,
                all_current_value_groups_available=covered == len(groups),
                selected_sources=len(selected), stale_or_ineligible_sources=len(ids-current_ids),
                required_slot_precision=relevant / len(selected) if selected else 0.,
                false_affordance=bool(set(apparent) - set(truth)),
                apparent_eligible_templates=sorted(apparent), true_eligible_templates=sorted(truth))


def analyze(run, output):
    output.mkdir(parents=True, exist_ok=False)
    source = run / 'attempts.jsonl'
    manifest = json.loads((run / 'manifest.json').read_text())
    if not manifest['complete']:
        raise ValueError('incomplete source run')
    data_path = ROOT / 'data/study/main-v1'
    for name, digest in manifest['dataset_manifest']['files'].items():
        if hashlib.sha256((data_path / name).read_bytes()).hexdigest() != digest:
            raise ValueError('frozen source data changed')
    data = json.loads((data_path / 'inputs.json').read_text())
    worlds = {w['id']: w for w in data['worlds']}
    queries = {x['id']: x['query'] for x in data['queries']}
    terminals = {}
    for line in source.read_text().splitlines():
        row = json.loads(line)
        if row['status'] in ['completed', 'failed']:
            if row['attempt_id'] in terminals:
                raise ValueError('duplicate terminal outcome')
            terminals[row['attempt_id']] = row
    rows = []
    for plan in manifest['planned']:
        r = terminals.get(plan['attempt_id'], {})
        q = queries[plan['case_id']]
        w = worlds[q['world']]
        m = context_metrics(w['events'], q, w['catalog'], r.get('evidence_ids', []))
        rows.append(dict(plan, family=w['family'], status=r.get('status', 'missing'), **m,
                         reader_correct=bool(r.get('score', {}).get('decision_correct'))))
    methods = {}
    world_values = {}
    for name in sorted({r['method'] for r in rows}):
        rs = [r for r in rows if r['method'] == name]
        ps = [r for r in rs if r['answerable']]
        grouped = defaultdict(list)
        for r in ps:
            grouped[r['world']].append(int(r['complete_positive_support']))
        world_values[name] = {w: statistics.mean(v) for w, v in grouped.items()}
        supported = [r for r in ps if r['complete_positive_support']]
        methods[name] = dict(cases=len(rs), positive_cases=len(ps),
            complete_positive_support=sum(r['complete_positive_support'] for r in ps),
            positive_support_rate=statistics.mean(r['complete_positive_support'] for r in ps),
            reader_success_given_complete_support=sum(r['reader_correct'] for r in supported),
            reader_given_complete_support_denominator=len(supported),
            false_affordance_cases=sum(r['false_affordance'] for r in rs),
            stale_or_ineligible_sources=sum(r['stale_or_ineligible_sources'] for r in rs),
            mean_current_value_group_coverage=statistics.mean(r['current_value_group_coverage'] for r in rs
                                                            if r['current_value_group_coverage'] is not None))
    contrasts = {}
    families = {w: v['family'] for w, v in worlds.items()}
    for other in sorted(methods):
        if other == 'typed':
            continue
        values = {w: world_values['typed'][w] - world_values[other][w]
                  for w in world_values['typed']}
        contrasts['typed minus ' + other] = dict(mean=statistics.mean(values.values()),
                                                world_bootstrap_ci95=paired_ci(values, families))
    summary = dict(created_at=datetime.now(timezone.utc).isoformat(),
        status='post-hoc exploratory reanalysis after seeing v1 outcomes; not a new frozen main study',
        source_attempts_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        methods=methods, exploratory_context_contrasts=contrasts,
        limits=['Same typed facts and common current-view/access filter for every v1 adapter.',
                'Conditioning reader success on available evidence is descriptive, not causal mediation.',
                'False affordance counts apparently eligible alternatives created by incomplete evidence.',
                'These adapters are not complete market memory products; all 12 company worlds are fictional.'])
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'per-query.jsonl').write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in rows))
    print(json.dumps({'output': str(output), 'rows': len(rows), 'methods': methods}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    analyze(a.run, a.output)
