#!/usr/bin/env python3
"""Recompute integrated outcomes from immutable actual provider traces."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import random
import statistics
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import ROOT,ARMS,canonical,sha

def paired_bootstrap(values,families,draws=10000,seed=202610223):
    groups=defaultdict(list)
    for world,value in values.items():groups[families[world]].append(value)
    rng=random.Random(seed);resamples=[]
    for _ in range(draws):
        sample=[rng.choice(group) for name,group in sorted(groups.items()) for _ in group]
        resamples.append(statistics.mean(sample))
    resamples.sort()
    return [resamples[int(.025*draws)],resamples[int(.975*draws)]]

def sign_p(values):
    positive=sum(v>0 for v in values);negative=sum(v<0 for v in values);n=positive+negative
    if not n:return 1.0
    tail=sum(math.comb(n,k) for k in range(min(positive,negative)+1))/(2**n)
    return min(1.0,2*tail)

def analyze(run,data_root,output):
    output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((run/'manifest.json').read_text());data=json.loads((data_root/'inputs.json').read_text())
    if manifest['data_sha256']!=sha((data_root/'inputs.json').read_bytes()):raise ValueError('data hash mismatch')
    labels={x['id']:x for x in json.loads((data_root/'labels.json').read_text())}
    families={w['id']:w['family'] for w in data['worlds']}
    ledger=[json.loads(line) for line in (run/'attempts.jsonl').read_text().splitlines()]
    done={}
    for row in ledger:
        if row['status'] not in ['completed','failed','interrupted']:continue
        if row['id'] in done:raise ValueError('duplicate terminal attempt')
        done[row['id']]=row
    rows=[]
    for plan in manifest['planned']:
        row=done.get(plan['id'],{});label=labels[plan['case_id']];score=row.get('raw_score',{});checked=row.get('validated_score',{})
        rows.append({k:plan[k] for k in ['id','case_id','world','arm','provider','evidence_bytes']} |
            {'condition':label['condition'],'family':label['family'],'positive':label['positive'],
             'status':row.get('status','not_attempted'),'correct':int(score.get('decision_correct',False)),
             'supported':int(score.get('supported_recommendation',False)),
             'recommended':int(score.get('recommended',False)),
             'unsupported':int(score.get('recommended',False) and not score.get('supported_recommendation',False)),
             'withheld':int(score.get('schema_valid',False) and not score.get('recommended',False)),
             'correct_withhold':int(score.get('correct_withhold',False)),
             'inappropriate_abstention':int(score.get('inappropriate_abstention',False)),
             'validated_correct':int(checked.get('decision_correct',False)),
             'validator_rejected':int(row.get('validator_rejected',False)),
             'complete_support':int(plan['context']['complete_positive_support']),
             'false_affordance':int(plan['context']['false_affordance']),
             'value_group_coverage':plan['context']['current_value_group_coverage'],
             'input_tokens':row.get('accounting',{}).get('total_input_tokens'),
             'output_tokens':row.get('accounting',{}).get('output_tokens'),
             'estimated_usd':float(row.get('accounting',{}).get('estimated_usd',0)),
             'seconds':row.get('seconds'),'violations':score.get('violations',[])})
    groups={};world_rates={}
    for provider in sorted({r['provider'] for r in rows}):
        for arm in ARMS:
            rs=[r for r in rows if r['provider']==provider and r['arm']==arm]
            if not rs:continue
            positives=[r for r in rs if r['positive']];negatives=[r for r in rs if not r['positive']]
            def total(key):return sum(r[key] for r in rs)
            rates={world:statistics.mean(r['correct'] for r in rs if r['world']==world) for world in families}
            world_rates[provider,arm]=rates
            known=[r for r in rs if r['input_tokens'] is not None]
            groups[provider+'/'+arm]={'cases':len(rs),'positive_cases':len(positives),'negative_cases':len(negatives),
                'correct':total('correct'),'correct_rate':total('correct')/len(rs),
                'correct_world_ci95':paired_bootstrap(rates,families),
                'supported':total('supported'),'supported_positive_rate':sum(r['supported'] for r in positives)/len(positives),
                'recommended':total('recommended'),'unsupported':total('unsupported'),
                'negative_recommendations':sum(r['recommended'] for r in negatives),
                'inappropriate_abstentions':sum(r['inappropriate_abstention'] for r in positives),
                'correct_withhold':total('correct_withhold'),'failures':sum(r['status']!='completed' for r in rs),
                'complete_support':sum(r['complete_support'] for r in positives),
                'complete_support_rate':sum(r['complete_support'] for r in positives)/len(positives),
                'false_affordance':total('false_affordance'),'validated_correct':total('validated_correct'),
                'validator_rejected':total('validator_rejected'),'estimated_usd':total('estimated_usd'),
                'usage_known_count':len(known),'input_tokens':sum(r['input_tokens'] for r in known),
                'output_tokens':sum(r['output_tokens'] for r in known),
                'mean_input_tokens':statistics.mean(r['input_tokens'] for r in known) if known else None,
                'mean_seconds':statistics.mean(r['seconds'] for r in rs if r['seconds'] is not None) if any(r['seconds'] is not None for r in rs) else None,
                'mean_evidence_bytes':statistics.mean(r['evidence_bytes'] for r in rs)}
    contrasts={}
    for provider in sorted({r['provider'] for r in rows}):
        for arm in ARMS:
            if arm=='specialized':continue
            differences={w:world_rates[provider,'specialized'][w]-world_rates[provider,arm][w] for w in families}
            contrasts[provider+'/specialized-minus-'+arm]={
                'difference':statistics.mean(differences.values()),'ci95':paired_bootstrap(differences,families),
                'world_differences':differences,'sd_world_difference':statistics.stdev(differences.values()) if len(differences)>1 else None,
                'exact_paired_sign_test_p_two_sided':sign_p(differences.values()),
                'scope':'primary within-model contrast' if arm=='generic' else 'secondary descriptive contrast'}
    primary=sorted([(v['exact_paired_sign_test_p_two_sided'],k) for k,v in contrasts.items() if k.endswith('minus-generic')])
    prior=0
    for index,(p,k) in enumerate(primary):
        adjusted=max(prior,min(1,p*(len(primary)-index)));prior=adjusted;contrasts[k]['holm_p']=adjusted
    sds=[contrasts[k]['sd_world_difference'] for _,k in primary]
    raw_n=math.ceil((1.96*max(sds)/.075)**2)
    selected=min(60,max(24,3*math.ceil(raw_n/3)))
    summary={'created_at':datetime.now(timezone.utc).isoformat(),'run_status':manifest['status'],'worlds':len(families),
        'planned_calls':len(rows),'completed':sum(r['status']=='completed' for r in rows),'failed_or_missing':sum(r['status']!='completed' for r in rows),
        'groups':groups,'contrasts':contrasts,'cost_estimate_usd':sum(r['estimated_usd'] for r in rows),
        'billed_cost_verified':False,'primary_correction':'Holm over two exact paired sign tests; CIs are per-contrast family-stratified world bootstrap.',
        'prospective_size_rule':{'max_pilot_world_sd':max(sds),'target_normal_halfwidth':.075,'unclipped_n':raw_n,'selected_worlds':selected,'note':'Use only for pilot; main results never change sample size.'},
        'evidence_sha256':{'manifest':sha((run/'manifest.json').read_bytes()),'ledger':sha((run/'attempts.jsonl').read_bytes()),'inputs':sha((data_root/'inputs.json').read_bytes()),'labels':sha((data_root/'labels.json').read_bytes())},
        'analysis_sha256':sha(Path(__file__).read_bytes()),'limits':['Fictional repeated templates, not real-company sampling.','Eligibility and evidence grounding, not revenue or optimal strategy.','No context is an information reference, not specialization evidence.','Native search component and lossless structured files, not whole-product ranking.']}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'per-attempt.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows))
    print(canonical({k:summary[k] for k in ['run_status','worlds','planned_calls','completed','failed_or_missing','cost_estimate_usd','prospective_size_rule']}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['run','data','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();analyze(a.run,a.data,a.output)
