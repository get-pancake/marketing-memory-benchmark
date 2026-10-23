#!/usr/bin/env python3
"""Execute saved proposed workflows in an in-memory mock capability environment.

This post-hoc consistency diagnostic reads supplied context only. It does not
measure provider efficacy, campaign outcomes, or add missing evidence.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import ROOT,canonical,sha
from study.contract import sql_oracle

def execute(proposal,evidence,q,catalog):
    if proposal.get('status')!='recommend':return {'status':'not_requested','calls':[],'units':0}
    calls=[];spent=0
    try:
        actions=proposal['plays']
        if len(actions)!=1:raise ValueError('one_action_required')
        action=actions[0];t=next(t for t in catalog if t['id']==action['template'])
        if t['objective']!=q['objective']:raise ValueError('wrong_objective')
        ids=set(action['evidence']);available={e['id']:e for e in evidence}
        if not ids<=set(available):raise ValueError('unavailable_citation')
        report=None
        for step in t['workflow']:
            if spent+1>q['max_units']:raise ValueError('budget_exhausted')
            spent+=1
            if step=='research_account':
                records=[e for e in evidence if e['entity']==q['account']]
                calls.append({'capability':step,'returned_ids':sorted(e['id'] for e in records),'source':'supplied fictional observation store'})
            elif step=='verify_prerequisites':
                local=[dict(e,supersedes=[]) for e in evidence if e['id'] in ids]
                applicable=sql_oracle(local,q,catalog)
                if t['id'] not in applicable:raise ValueError('supplied_citations_do_not_satisfy_contract')
                calls.append({'capability':step,'verdict':'satisfied','sources':sorted(ids)})
            elif step=='prepare_evidence_report':
                if not any(c['capability']=='verify_prerequisites' for c in calls):raise ValueError('unverified_report')
                report={'account':q['account'],'objective':q['objective'],'template':t['id'],
                    'source_ids':sorted(ids),'policy_versions':sorted(i for i in ids if available[i]['authority']=='approved')}
                calls.append({'capability':step,'report_sha256':sha(canonical(report).encode())})
            else:raise ValueError('unavailable_capability')
        if report is None or spent!=t['units']:raise ValueError('resource_or_output_mismatch')
        return {'status':'completed','calls':calls,'units':spent,'report':report}
    except (ValueError,KeyError,StopIteration) as e:
        return {'status':'rejected','calls':calls,'units':spent,'reason':str(e)}

def replay(run,data_root,output):
    output.mkdir(parents=True,exist_ok=False)
    data=json.loads((data_root/'inputs.json').read_text());worlds={w['id']:w for w in data['worlds']};cases={c['id']:c for c in data['queries']}
    manifest=json.loads((run/'manifest.json').read_text());rows=[]
    for plan in manifest['planned']:
        row=json.loads((run/plan['id']/'result.json').read_text());c=cases[plan['case_id']];w=worlds[plan['world']]
        evidence=[e for e in w['events'] if e['id'] in plan['evidence_ids']]
        result=execute(row.get('materialized',{}),evidence,c['query'],w['catalog'])
        rows.append({k:plan[k] for k in ['id','provider','arm','case_id']} | result)
    summary={'kind':'post-hoc mock execution consistency; no external provider actions or commercial outcomes',
        'cases':len(rows),'proposed':sum(r['status']!='not_requested' for r in rows),
        'completed':sum(r['status']=='completed' for r in rows),'rejected':sum(r['status']=='rejected' for r in rows),
        'capability_calls':sum(len(r['calls']) for r in rows),'external_network_calls':0,
        'run_manifest_sha256':sha((run/'manifest.json').read_bytes()),'executor_sha256':sha(Path(__file__).read_bytes())}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'receipts.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows));print(canonical(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['run','data','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();replay(a.run,a.data,a.output)
