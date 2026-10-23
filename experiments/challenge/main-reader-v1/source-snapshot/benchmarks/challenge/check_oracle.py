"""Independent SQL current-view/eligibility and exhaustive optimization check."""
import argparse,json,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.challenge.core import CATALOG,canonical,dump,visible,candidates,optimize,enumerate_optimum

def sql_reference(case):
    db=sqlite3.connect(':memory:')
    db.executescript('CREATE TABLE events(id TEXT, entity TEXT, relation TEXT, value TEXT, authority TEXT, valid_day INT, observed_day INT, access TEXT, supersedes TEXT); CREATE TABLE accounts(account TEXT); CREATE TABLE catalog(action TEXT, cost INT, multiplier INT, signals TEXT, extra TEXT);')
    db.executemany('INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)',[(e['id'],e['entity'],e['relation'],canonical(e['value']),e['authority'],e['valid_day'],e['observed_day'],e['access'],canonical(e.get('supersedes',[]))) for e in case['events']])
    db.executemany('INSERT INTO accounts VALUES (?)',[(a,) for a in case['query']['accounts']])
    db.executemany('INSERT INTO catalog VALUES (?,?,?,?,?)',[(t['id'],t['cost'],t['multiplier'],canonical(t['signals']),canonical(t['extra'])) for t in CATALOG])
    db.execute('CREATE TEMP VIEW current AS SELECT e.* FROM events e WHERE e.valid_day<=30 AND e.observed_day<=30 AND e.access="public" AND NOT EXISTS(SELECT 1 FROM events newer, json_each(newer.supersedes) old WHERE old.value=e.id AND newer.entity=e.entity AND newer.relation=e.relation AND newer.authority=e.authority AND newer.valid_day<=30 AND newer.observed_day<=30 AND newer.access="public")')
    # This standalone reference intentionally supports the frozen day/access
    # contract, failing rather than silently applying it to another protocol.
    if case['query']['day']!=30 or case['query']['access']!=['public']:raise ValueError('SQL reference boundary unsupported')
    db.execute('CREATE TEMP VIEW unambiguous AS SELECT entity,relation,authority,MIN(value) value FROM current GROUP BY entity,relation,authority HAVING COUNT(DISTINCT value)=1')
    query='''SELECT a.account,t.action,t.cost,json_extract(priority.value,'$')*t.multiplier
      FROM accounts a CROSS JOIN catalog t
      JOIN unambiguous policy ON policy.entity='seller' AND policy.relation='policy' AND policy.authority='approved'
      JOIN unambiguous profile ON profile.entity=a.account AND profile.relation='profile' AND profile.authority='observed'
      JOIN unambiguous consent ON consent.entity=a.account AND consent.relation='consent' AND consent.authority='observed'
      JOIN unambiguous signal ON signal.entity=a.account AND signal.relation='signal' AND signal.authority='observed'
      JOIN unambiguous priority ON priority.entity=a.account AND priority.relation='priority' AND priority.authority='approved'
      JOIN unambiguous initiative ON initiative.entity=a.account AND initiative.relation='initiative' AND initiative.authority='observed'
      JOIN unambiguous need ON need.entity=json_extract(initiative.value,'$') AND need.relation='need' AND need.authority='observed'
      JOIN unambiguous offering ON offering.entity=json_extract(need.value,'$') AND offering.relation='offering' AND offering.authority='observed'
      JOIN unambiguous proof ON proof.entity=json_extract(offering.value,'$') AND proof.relation='proof' AND proof.authority='observed'
      JOIN unambiguous verified ON verified.entity=json_extract(proof.value,'$') AND verified.relation='verified' AND verified.authority='approved'
      WHERE json_extract(profile.value,'$.region') IN (SELECT value FROM json_each(policy.value,'$.allowed_regions'))
      AND json_extract(profile.value,'$.sector') NOT IN (SELECT value FROM json_each(policy.value,'$.blocked_sectors'))
      AND t.action IN (SELECT value FROM json_each(policy.value,'$.actions'))
      AND consent.value='true' AND verified.value='true' AND json_type(priority.value)='integer'
      AND json_extract(priority.value,'$')>=0
      AND json_extract(signal.value,'$') IN (SELECT value FROM json_each(t.signals))
      AND NOT EXISTS (SELECT 1 FROM json_each(t.extra) extra WHERE NOT EXISTS (
        SELECT 1 FROM unambiguous prerequisite WHERE prerequisite.relation=extra.value
        AND prerequisite.entity=CASE WHEN extra.value='shareable' THEN json_extract(proof.value,'$') ELSE json_extract(offering.value,'$') END
        AND prerequisite.authority='approved' AND prerequisite.value='true'))'''
    items=[dict(account=a,action=b,cost=c,value=d) for a,b,c,d in db.execute(query)]
    current={x[0] for x in db.execute('SELECT id FROM current')};db.close();return current,items

def check(data,output):
    rows=[]
    for entry in json.loads((data/'index.json').read_text())['cases']:
        case=json.loads((data/entry['path']).read_text());current,sql=sql_reference(case)
        actual=candidates(visible(case['events'],case['query']),case['query'])
        clean=lambda xs:sorted((x['account'],x['action'],x['cost'],x['value']) for x in xs)
        if clean(sql)!=clean(actual) or current!={e['id'] for e in visible(case['events'],case['query'])}:raise AssertionError(case['id'])
        brute=enumerate_optimum(sql,case['query']['budget']);dynamic=optimize(actual,case['query']['budget'])['value']
        if brute!=dynamic:raise AssertionError('optimizer disagreement')
        rows.append({'case_id':case['id'],'eligible':len(sql),'optimum':brute,'passed':True})
    dump(output,{'status':'passed','cases':len(rows),'sql_and_dynamic_programming_agree':True,'exhaustive_optima_agree':True,'independent_human_validation':False,'rows':rows})
    print(canonical({'oracle_check':'passed','cases':len(rows)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();check(a.data,a.output)
