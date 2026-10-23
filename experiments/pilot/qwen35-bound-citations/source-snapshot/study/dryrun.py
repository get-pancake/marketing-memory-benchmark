"""Executable mock-provider research environment; no network or production writes."""
from .contract import applicable, canonical
import hashlib

ALLOWED={'research_account','verify_prerequisites','prepare_evidence_report'}


def execute(spec, evidence, query, catalog):
    if spec['allowed_next_step']!='dry_run' or not set(spec['steps'])<=ALLOWED:
        raise ValueError('unsupported workflow')
    if len(spec['steps'])!=spec['units'] or spec['units']>query['max_units']:
        raise ValueError('mock resource accounting disagrees with catalog')
    receipts=[]
    for step in spec['steps']:
        if step=='research_account':
            result={'observations':[e['id'] for e in evidence if e['entity']==query['account'] and e['authority']=='observed']}
        elif step=='verify_prerequisites':
            groups=applicable(evidence,query,catalog).get(spec['template'],[])
            result={'satisfied':bool(groups) and all(set(spec['evidence']) & g for g in groups)}
            if not result['satisfied']:raise ValueError('mock prerequisite verification failed')
        else:
            result={'account':query['account'],'objective':query['objective'],
                    'sources':spec['evidence'],'policy_versions':spec['policy_versions'],
                    'mechanism_hypothesis':spec['mechanism_hypothesis']}
        receipts.append({'capability':step,'units':1,'result':result,
            'receipt_hash':hashlib.sha256(canonical([step,result]).encode()).hexdigest()})
    return dict(kind='executed_mock_provider_dry_run',status='completed',units=sum(r['units'] for r in receipts),receipts=receipts)
