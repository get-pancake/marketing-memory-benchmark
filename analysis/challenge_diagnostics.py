"""Post-hoc descriptive failure localization; no changed primary outcomes."""
import argparse,json,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import dump,sha,candidates,visible,optimize,gold
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows=json.loads((ROOT/'analysis/challenge/main-v1/per-attempt.json').read_text());index=json.loads((ROOT/'data/challenge/main-v1/index.json').read_text())
    cases={e['id']:json.loads((ROOT/'data/challenge/main-v1'/e['path']).read_text()) for e in index['cases']}
    detailed=[];sensitivity=[]
    for r in sorted(rows,key=lambda x:x['id']):
        case=cases[r['case_id']];folder=ROOT/'experiments/challenge/main-reader-v1'/r['id'];result=json.loads((folder/'result.json').read_text())
        packet=next(p for p in json.loads((ROOT/'experiments/challenge/main-context-v1'/r['case_id']/'packets.json').read_text()) if p['arm']==r['arm'])
        events=visible(case['events'],case['query']);byid={e['id']:e for e in events};ev=[byid[i] for i in packet['evidence_ids']]
        items={(i['account'],i['action']):i for i in candidates(ev,case['query'])};output=result.get('output',{});acts=output.get('actions',[])
        valid=result['status']=='completed' and len(acts)<=3 and len({x['account'] for x in acts})==len(acts)
        value=0;cost=0;details=[]
        for action in acts:
            item=items.get((action['account'],action['action']))
            if item is None:valid=False
            else:
                value+=item['value'];cost+=item['cost'];cites=set(action['sources'])
                missing=[g for g in item['support_groups'] if not (set(g)&cites)]
                details.append({'account':action['account'],'action':action['action'],'value':item['value'],
                    'missing_citation_groups':[[{k:byid[i][k] for k in ['id','entity','relation','value']} for i in g] for g in missing],
                    'unsupplied_citations':sorted(cites-set(packet['evidence_ids']))})
        valid=valid and cost<=case['query']['budget'];value=value if valid else 0
        sensitivity.append({'id':r['id'],'provider':r['provider'],'arm':r['arm'],'world':r['world'],'optimum':r['optimum'],
                            'citation_relaxed_value':value,'normalized':value/r['optimum'] if r['optimum'] else None})
        if r['returned_value']<r['recoverable_value'] or r['unsafe']:
            detailed.append({'id':r['id'],'primary_score':r,'action_details':details,'output':output,'context_optimum_plan':optimize(list(items.values()),case['query']['budget']),
                'full_optimum':gold(case),'citation_relaxed_value':value,'response_path':str((folder/'response.json').relative_to(ROOT)),
                'response_sha256':sha((folder/'response.json').read_bytes()),'result_sha256':sha((folder/'result.json').read_bytes())})
    summaries=[]
    for provider in ['openai','anthropic']:
        for arm in ['none','company','gtm','markdown','gbrain','full']:
            base=[r for r in rows if r['provider']==provider and r['arm']==arm];sub=[r for r in sensitivity if r['provider']==provider and r['arm']==arm and r['normalized'] is not None]
            by=defaultdict(list)
            for r in sub:by[r['world']].append(r['normalized'])
            summaries.append({'provider':provider,'arm':arm,'cases':len(base),'positive_cases':len(sub),
                'context_below_full_positive':sum(r['optimum']>0 and r['recoverable_value']<r['optimum'] for r in base),
                'reader_below_context_positive':sum(r['optimum']>0 and r['returned_value']<r['recoverable_value'] for r in base),
                'unsafe':sum(r['unsafe'] for r in base),'error_counts':dict(Counter(e for r in base for e in r['errors'])),
                'citation_relaxed_company_mean':float(np.mean([np.mean(v) for v in by.values()])),
                'citation_relaxed_context_optimal':sum(r['citation_relaxed_value']==next(x['recoverable_value'] for x in base if x['id']==r['id']) for r in sub)})
    selected=[]
    for name,predicate in [
       ('company_missing_support',lambda c: c['optimum']>0 and c['arm']=='company' and c['recoverable_value']==0),
       ('specialized_budget_limit',lambda c: c['optimum']>0 and c['arm']=='gtm' and 0<c['recoverable_value']<c['optimum'])]:
        row=next(r for r in sorted(rows,key=lambda x:x['id']) if r['provider']=='openai' and predicate(r));cid=row['case_id'];case=cases[cid]
        comparisons=[{k:r[k] for k in ['arm','provider','optimum','recoverable_value','returned_value','errors']} for r in rows if r['case_id']==cid]
        selected.append({'category':name,'selection':'First lexicographic case satisfying the declared descriptive category, after main outcomes were available.','case_id':cid,'comparisons':comparisons,'reference_plan':gold(case)['reference_plan']})
    missing=Counter(x['relation'] for r in detailed for a1 in r['action_details'] for g in a1['missing_citation_groups'] for x in g)
    dump(a.output,{'scope':'Post-hoc descriptive diagnostics. Primary outcomes, denominators, code and tests unchanged. Citation-relaxed sensitivity requires context-supported eligibility and all global constraints but ignores citation bindings. No new inference or confirmatory tests.',
       'shortfall_attempts':len(detailed),'unsafe_attempts':sum(r['unsafe'] for r in rows),'missing_citation_relation_counts':dict(missing),'summary':summaries,'selected_examples':selected,'all_reader_shortfalls':detailed,
       'input_analysis_sha256':sha((ROOT/'analysis/challenge/main-v1/per-attempt.json').read_bytes()),'fresh_api_calls':0,'independent_human_review':False})
    print(json.dumps({'shortfalls':len(detailed),'unsafe':sum(r['unsafe'] for r in rows),'missing_citation_relations':dict(missing),'examples':[x['case_id'] for x in selected]}))
if __name__=='__main__':main()
