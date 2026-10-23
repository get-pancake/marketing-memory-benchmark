#!/usr/bin/env python3
"""Re-score saved model attempts and aggregate paired company-world evidence.

No model calls. Missing/failed attempts remain in their planned denominators.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from study.contract import score, canonical


def percentile(xs,p):
    if not xs:return None
    x=sorted(xs);k=(len(x)-1)*p;a=int(k);b=min(a+1,len(x)-1)
    return x[a]+(x[b]-x[a])*(k-a)


def paired_ci(values, families, seed=7201, draws=10000):
    """Family-stratified paired world bootstrap; never question-level pseudo-N."""
    if len(values)<6:return None
    groups=defaultdict(list)
    for world,value in values.items():groups[families[world]].append(value)
    rng=random.Random(seed)
    samples=[]
    for _ in range(draws):
        sample=[rng.choice(group) for group in groups.values() for _ in group]
        samples.append(statistics.mean(sample))
    return [percentile(samples,.025),percentile(samples,.975)]


def analyze(run_path,data_path,output_path):
    manifest=json.loads((run_path/'manifest.json').read_text())
    data=json.loads((data_path/'inputs.json').read_text())
    labels={r['id']:r for r in json.loads((data_path/'labels.json').read_text())}
    worlds={w['id']:w for w in data['worlds']}
    queries={c['id']:c['query'] for c in data['queries']}
    for name,digest in manifest['dataset_manifest']['files'].items():
        if hashlib.sha256((data_path/name).read_bytes()).hexdigest()!=digest:raise ValueError('dataset hash mismatch')
    planned_ids={r['attempt_id'] for r in manifest['planned']}
    if len(planned_ids)!=len(manifest['planned']):raise ValueError('duplicate planned attempt')
    attempts={};model_calls=set();reused_calls=set();origins={}
    for line in (run_path/'attempts.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r['attempt_id'] not in planned_ids:raise ValueError('unplanned attempt')
        if r['status']=='model_call_started':model_calls.add(r['attempt_id'])
        if r['status']=='model_call_reused':reused_calls.add(r['attempt_id'])
        if r['status'] in ['completed','failed']:
            if r['attempt_id'] in attempts:raise ValueError('duplicate terminal attempt')
            attempts[r['attempt_id']]=r
        for receipt in r.get('retrieval',{}).get('embedding_receipts',[]):
            origins[receipt['key']]=dict(kind=receipt['kind'],seconds=receipt.get('origin_seconds',receipt['seconds']))
    rows=[]
    for plan in manifest['planned']:
        r=attempts.get(plan['attempt_id'],{})
        cid=plan['case_id'];q=queries[cid];w=worlds[q['world']];label=labels[cid]
        saved=r.get('score',{})
        if r.get('output') is not None:
            evidence=[e for e in w['events'] if e['id'] in r['evidence_ids']]
            replay=score(r['output'],w['events'],evidence,q,w['catalog'],label['acceptable'],r.get('slot_bindings'))
            if replay!=saved:raise ValueError('saved score differs from replay')
        row=dict(plan,condition=label['condition'],family=label['family'],positive=label['positive'],
            status=r.get('status','missing'),decision_correct=int(bool(saved.get('decision_correct'))),
            choice_correct=int(bool(saved.get('choice_correct'))),schema_valid=int(bool(saved.get('schema_valid'))),
            supported=int(bool(saved.get('supported_recommendation'))),recommended=int(bool(saved.get('recommended'))),
            inappropriate_abstention=int(bool(saved.get('inappropriate_abstention'))),
            correct_withhold=int(bool(saved.get('correct_withhold'))),support_available=int(bool(r.get('support_available'))),
            dry_run_completed=int(r.get('dry_run_execution',{}).get('status')=='completed'),
            prompt_tokens=r.get('usage',{}).get('prompt_tokens'),completion_tokens=r.get('usage',{}).get('completion_tokens'),
            generation_seconds=r.get('generation_seconds'),retrieval_seconds=r.get('retrieval',{}).get('seconds'),
            model_request_reused=bool(r.get('model_request_reused')),
            physical_generation_seconds=r.get('physical_generation_seconds',r.get('generation_seconds')),
            duration_seconds=r.get('duration_seconds'),finish_reason=r.get('finish_reason'),
            violations=saved.get('violations',[]))
        if row['status']!='completed':
            # A software/inference failure cannot receive success merely because
            # a score was computed before a later execution/validation exception.
            row['decision_correct']=row['supported']=row['dry_run_completed']=0
        rows.append(row)
    bymethod=defaultdict(list)
    for row in rows:bymethod[row['method']].append(row)
    family_by_world={w:worlds[w]['family'] for w in {r['world'] for r in rows}}
    scores={};world_means={}
    for method,group in bymethod.items():
        positives=[r for r in group if r['positive']];negatives=[r for r in group if not r['positive']]
        grouped=defaultdict(list)
        for r in group:grouped[r['world']].append(r['decision_correct'])
        world_means[method]={w:statistics.mean(v) for w,v in grouped.items()}
        def rate(field,subset):return sum(r[field] for r in subset)/len(subset) if subset else None
        def total(field):return sum(r[field] for r in group if r[field] is not None)
        times=[r['generation_seconds'] for r in group if r['generation_seconds'] is not None]
        scores[method]=dict(planned=len(group),completed=sum(r['status']=='completed' for r in group),
            physical_calls=sum(r['attempt_id'] in model_calls for r in group),
            reused_requests=sum(r['attempt_id'] in reused_calls for r in group),
            failures=sum(r['status']!='completed' for r in group),worlds=len(grouped),positive_cases=len(positives),negative_cases=len(negatives),
            primary=rate('decision_correct',group),primary_world_ci95=paired_ci(world_means[method],family_by_world),
            applicable_choice=rate('choice_correct',group),schema_valid=rate('schema_valid',group),
            supported_positive_coverage=rate('supported',positives),positive_support_available=rate('support_available',positives),
            inappropriate_abstention=rate('inappropriate_abstention',positives),correct_negative_withhold=rate('correct_withhold',negatives),
            negative_recommendations=rate('recommended',negatives),positive_dry_run_completion=rate('dry_run_completed',positives),
            input_tokens=total('prompt_tokens'),output_tokens=total('completion_tokens'),
            generation_seconds=total('generation_seconds'),retrieval_seconds=total('retrieval_seconds'),
            generation_p50_seconds=percentile(times,.5),generation_p95_seconds=percentile(times,.95),
            truncations=sum(r['finish_reason']=='length' for r in group),
            violations=dict(Counter(v for r in group for v in r['violations'])),
            by_condition={c:{'n':len(rs),'correct':sum(r['decision_correct'] for r in rs)} for c in sorted({r['condition'] for r in group})
                          if (rs:=[r for r in group if r['condition']==c])})
    contrasts={}
    for left,right in [('typed','prompt_hybrid'),('typed','facet_hybrid'),('prompt_hybrid','generic_hybrid'),('typed','typed_history'),('full_context','typed')]:
        if left in world_means and right in world_means:
            if world_means[left].keys()!=world_means[right].keys():raise ValueError('unpaired worlds')
            diff={w:world_means[left][w]-world_means[right][w] for w in world_means[left]}
            contrasts[left+' minus '+right]=dict(mean=statistics.mean(diff.values()),ci95=paired_ci(diff,family_by_world),
                world_differences=diff,sd=statistics.stdev(diff.values()) if len(diff)>1 else None,
                inference='Paired world bootstrap stratified by family; exploratory except the predeclared primary contrast. No equivalence claim from nonsignificance.')
    transitions={}
    for method,group in bymethod.items():
        bywc={(r['world'],r['condition']):r for r in group}
        values={}
        for before,after in [('initial','weak_feedback'),('weak_feedback','policy_revision'),('policy_revision','account_requalified'),('account_requalified','evidence_correction')]:
            pairs=[(bywc[(w,before)],bywc[(w,after)]) for w in family_by_world if (w,before) in bywc and (w,after) in bywc]
            previous=sum(a['decision_correct'] for a,b in pairs)
            both=sum(a['decision_correct']*b['decision_correct'] for a,b in pairs)
            values[before+' -> '+after]=dict(world_pairs=len(pairs),correct_before=previous,correct_both=both,
                unconditional_joint=both/len(pairs) if pairs else None,conditional_preservation_or_refresh=both/previous if previous else None)
        transitions[method]=values
    result=dict(schema='study-analysis-v1',analyzed_at=datetime.now(timezone.utc).isoformat(),
        run=str(run_path),dataset=str(data_path),source_run_complete=manifest['complete'],
        planned_attempts=len(rows),recorded_terminal_attempts=len(attempts),model_calls_started=len(model_calls),
        reused_identical_requests=len(reused_calls),
        physical_calls_with_unknown_usage=sum(r['attempt_id'] in model_calls and (r['prompt_tokens'] is None or r['completion_tokens'] is None) for r in rows),
        physical_generation_seconds=sum(r['physical_generation_seconds'] for r in rows if r['physical_generation_seconds'] is not None),
        physical_input_tokens=sum(r['prompt_tokens'] for r in rows if not r['model_request_reused'] and r['prompt_tokens'] is not None),
        physical_output_tokens=sum(r['completion_tokens'] for r in rows if not r['model_request_reused'] and r['completion_tokens'] is not None),
        cost_accounting_note='Per-method token and generation-time totals charge the observed origin call for identical-request reuse. Physical calls/tokens/time are reported separately; a reused response is not fresh inference. Missing usage is unknown, not proof of zero compute.',
        methods=scores,paired_contrasts=contrasts,world_means=world_means,transitions=transitions,
        unique_embedding_origin_seconds={k:sum(r['seconds'] for r in origins.values() if r['kind']==k) for k in ['event','query']},
        embedding_cost_note='Unique observed cache origins across this run, counted once; common reusable index cost, not a per-method cache-order advantage. Infrastructure dollars/energy unknown.',
        uncertainty_note='Conditional on fictional generator/families and tested model. World bootstrap does not represent commercial-population uncertainty. Fewer than six worlds: descriptive pilot, CI suppressed. Degenerate bootstrap intervals are not guarantees.',
        analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    output_path.mkdir(parents=True,exist_ok=True)
    (output_path/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (output_path/'per-attempt.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows))
    print(json.dumps({'planned':len(rows),'terminal':len(attempts),'methods':{m:s['primary'] for m,s in scores.items()},'output':str(output_path)}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();analyze(a.run,a.data,a.output)
