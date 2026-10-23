"""Original fictional event worlds; construction labels are not model judgments."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random

from .contract import canonical, applicable, visible, sql_oracle

FAMILIES = {
 'hiring': [('observed_signal','hiring'),('offering_pain','onboarding'),('proof_for_pain','onboarding')],
 'migration': [('observed_signal','migration'),('offering_pain','integration'),('proof_for_pain','integration')],
 'renewal': [('customer_state','active'),('usage_trend','declining'),('offering_pain','adoption'),('proof_for_pain','adoption')],
 'partner': [('partner_status','verified'),('channel_fit','reseller'),('offering_pain','integration'),('proof_for_pain','integration')],
 'compliance': [('certification','ISO27001'),('observed_signal','compliance_review'),('offering_pain','audit_effort'),('proof_for_pain','audit_effort')],
}
CONDITIONS = ['initial','weak_feedback','policy_revision','account_requalified','evidence_correction','restricted_evidence','objective_change','policy_conflict']


def build(split, count, seed):
    rng = random.Random(seed)
    worlds, queries, labels = [], [], []
    families = ['hiring','migration'] if split == 'pilot' else ['renewal','partner','compliance']
    for w in range(count):
        world = 'w' + hashlib.sha256(f'{split}:{seed}:{w}'.encode()).hexdigest()[:8]
        account = rng.choice(['Velora','Norvale','Arden','Caldera','Oriole','Ilex']) + '-' + str(rng.randrange(100,999))
        family = families[w % len(families)]
        role = rng.choice(['operations_director','revenue_lead','IT_manager','commercial_director'])
        geo, new_geo = rng.sample(['EU','UK','US','CA'],2)
        # World-specific monotone dates and template-ID permutations prevent
        # public date/ID constants from directly revealing condition labels.
        day_map={1:rng.randrange(50,900)}
        for day in range(2,7):day_map[day]=day_map[day-1]+rng.randrange(1,8)
        day_map[99]=day_map[6]+rng.randrange(100,300)
        template_ids=['P1','P2','P3','P4'];rng.shuffle(template_ids)
        template_map=dict(zip(['P1','P2','P3','P4'],template_ids))
        max_units=rng.choice([2,3])
        records = []
        def add(entity,key,value,authority='observed',day=1,valid=None,scopes=None,old=None):
            eid = 'e' + hashlib.sha256(f'{world}:{len(records)}:{seed}'.encode()).hexdigest()[:7]
            records.append(dict(id=eid,world=world,entity=entity,key=key,value=value,authority=authority,
                valid=day_map[day if valid is None else valid],observed=day_map[day],scopes=['sales'] if scopes is None else scopes,
                supersedes=[] if old is None else [old],source='fictional_record_'+eid))
            return eid
        pr=add('seller','approved_role',role,'approved')
        pg=add('seller','approved_geo',geo,'approved')
        add(account,'account_role',role)
        ag=add(account,'account_geo',geo)
        req = [dict(entity='seller',key='approved_role',authority='approved'),dict(entity='seller',key='approved_geo',authority='approved'),
               dict(entity='$account',key='account_role',authority='observed'),dict(entity='$account',key='account_geo',authority='observed')]
        special_ids=[]
        for key,value in FAMILIES[family]:
            entity = 'seller' if key in ['offering_pain','proof_for_pain'] else account
            eid=add(entity,key,value,scopes=['sales','proof'] if key=='proof_for_pain' else None)
            special_ids.append(eid)
            req.append(dict(entity='$account' if entity==account else entity,key=key,authority='observed',equals=value))
        primary = dict(id='P1',objective=family,requirements=req,equalities=[[0,2],[1,3]],units=3,
            workflow=['research_account','verify_prerequisites','prepare_evidence_report'],
            mechanism=f'The observed {family} context may justify a scoped research review; commercial value is unproven.')
        alternate = dict(primary,id='P2',units=2,workflow=['verify_prerequisites','prepare_evidence_report'])
        diagnostic = dict(id='P3',objective='qualification_audit',requirements=req[:4],equalities=[[0,2],[1,3]],units=2,
            workflow=['verify_prerequisites','prepare_evidence_report'],mechanism='Check current targeting fit before further research.')
        # A catalog alternative with an unmet prerequisite tests applicable sets.
        decoy = dict(primary,id='P4',requirements=req+[dict(entity='$account',key='procurement_stage',authority='observed',equals='approved')])
        catalog=[primary,alternate,diagnostic,decoy]
        for t in catalog:t['id']=template_map[t['id']]
        rng.shuffle(catalog)
        noise_count = [12,20,28,36][w % 4]
        for i in range(noise_count):
            key=rng.choice(['meeting_note','industry_context','planning_note','unapproved_strategy','past_campaign'])
            add(rng.choice([account,'seller']),key,
                f'{family} {account}: '+rng.choice(['research discussed without a verified signal','generic market discussion, no policy decision',
                'the offering and buyer pain were mentioned, not approved','review could be useful; prerequisites still need checking']),
                authority='hypothesis' if key=='unapproved_strategy' else 'observed')
        # Repeated valid records test redundancy. They do not create new facts.
        # Only immutable role and offering pain are duplicated (never updated below).
        for i in range(w % 3):
            add(account,'account_role',role)
            add('seller','offering_pain',dict(FAMILIES[family])['offering_pain'])
        add(account,'non_response','No reply after one unconfirmed contact attempt.',day=2)
        add('seller','approved_geo',new_geo,'proposal',day=2)  # Not policy.
        add('seller','approved_geo',new_geo,'approved',day=3,old=pg)
        add(account,'account_geo',new_geo,day=4,old=ag)
        first_key=FAMILIES[family][0][0]
        add(account,first_key,'withdrawn',day=5,valid=1,old=special_ids[0])
        add('seller','approved_role','unrelated_role','approved',day=6)  # Unsuperseded conflict.
        # Explicit future and cross-scope witnesses must never enter the input.
        add(account,first_key,FAMILIES[family][0][1],day=99)
        add(account,'procurement_stage','approved',scopes=['executive'])
        rng.shuffle(records)
        worlds.append(dict(id=world,family=family,events=records,catalog=catalog))
        for j,condition in enumerate(CONDITIONS):
            day=[1,2,3,4,5,2,4,6][j]
            q=dict(world=world,account=account,objective='qualification_audit' if j==6 else family,
                   known_at=day_map[day],valid_at=day_map[4 if j==4 else day],scopes=['sales'] if j==5 else ['sales','proof'],max_units=max_units)
            qid='q'+hashlib.sha256(f'{world}:{j}'.encode()).hexdigest()[:10]
            queries.append(dict(id=qid,query=q))
            logical=['P3'] if j==6 else ((['P1','P2'] if max_units==3 else ['P2']) if j in [0,1,3] else [])
            expected=sorted(template_map[t] for t in logical)
            if sorted(applicable(visible(records,q),q,catalog)) != sorted(expected) or sql_oracle(records,q,catalog) != sorted(expected):
                raise AssertionError('construction label / Python / SQL disagreement')
            labels.append(dict(id=qid,world=world,condition=condition,family=family,acceptable=expected,
                positive=bool(expected),noise_events=noise_count))
    return dict(worlds=worlds,queries=queries), labels


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--split',choices=['pilot','test'],required=True)
    p.add_argument('--worlds',type=int,required=True)
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.worlds<=0: p.error('positive world count required')
    a.output.mkdir(parents=True,exist_ok=False)
    inputs,labels=build(a.split,a.worlds,a.seed)
    hashes={}
    for name,x in [('inputs.json',inputs),('labels.json',labels)]:
        data=(canonical(x)+'\n').encode()
        (a.output/name).write_bytes(data)
        hashes[name]=hashlib.sha256(data).hexdigest()
    manifest=dict(schema='gtm-verified-events-v1',split=a.split,worlds=a.worlds,queries=len(labels),seed=a.seed,
        created_at=datetime.now(timezone.utc).isoformat(),files=hashes,
        provenance='Original programmatically authored fictional worlds; no customer data, human annotations or model-generated fact prose.',
        checks='Construction labels agree with independent Python and SQLite contract implementations; not human validation.',
        license='CC-BY-4.0',scope='Verified-event controlled experiment, not raw-document ingestion or commercial outcomes.')
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest))


if __name__=='__main__': main()
