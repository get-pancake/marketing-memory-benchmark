"""Public Play contract, causal view and strict executable support checking."""
from collections import defaultdict
import json
import sqlite3


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def visible(events, q, retain_superseded=False):
    by_id = {e['id']: e for e in events}
    if len(by_id) != len(events):
        raise ValueError('duplicate event ID')
    for e in events:
        for old in e['supersedes']:
            p = by_id[old]
            if any(p[k] != e[k] for k in ['world', 'entity', 'key', 'authority']) or p['observed'] >= e['observed']:
                raise ValueError('invalid supersession')
    eligible = [e for e in events if e['world'] == q['world'] and e['observed'] <= q['known_at']
                and e['valid'] <= q['valid_at'] and set(e['scopes']) <= set(q['scopes'])]
    old = set() if retain_superseded else {i for e in eligible for i in e['supersedes']}
    return sorted([e for e in eligible if e['id'] not in old], key=lambda e: e['id'])


def requirements(t, q):
    return [(q['account'] if r['entity'] == '$account' else r['entity'], r['key'], r['authority'])
            for r in t['requirements']]


def slot_name(r):
    return f"{'account' if r['entity']=='$account' else r['entity']}.{r['key']}:{r['authority']}"


def applicable(events, q, catalog):
    """Return all valid alternatives and their acceptable evidence groups.

    Any conflicting value at the same entity/key/authority blocks that slot.
    Required equalities link approved seller policy and account observations.
    Supplied events must first pass the shared visibility boundary.
    """
    groups = defaultdict(list)
    for e in events:
        groups[(e['entity'], e['key'], e['authority'])].append(e)
    result = {}
    for t in catalog:
        if t['objective'] != q['objective'] or t['units'] > q['max_units']:
            continue
        reqs = requirements(t, q)
        slots = [groups[k] for k in reqs]
        if any(not g or len({e['value'] for e in g}) != 1 for g in slots):
            continue
        values = [g[0]['value'] for g in slots]
        if any('equals' in r and values[i] != r['equals'] for i, r in enumerate(t['requirements'])):
            continue
        if any(values[a] != values[b] for a, b in t['equalities']):
            continue
        result[t['id']] = [set(e['id'] for e in g) for g in slots]
    return result


def sql_oracle(events, q, catalog, witnesses=False):
    """Independent SQL implementation of time, permissions, uniqueness and joins.

    It deliberately calls neither visible() nor applicable(). This is software
    cross-validation, not an independently authored or human-reviewed benchmark.
    """
    db = sqlite3.connect(':memory:')
    db.executescript('''CREATE TABLE events(id TEXT PRIMARY KEY, world TEXT, entity TEXT,
      key TEXT, value TEXT, authority TEXT, valid INTEGER, observed INTEGER);
      CREATE TABLE scope(id TEXT, permission TEXT); CREATE TABLE permits(permission TEXT);
      CREATE TABLE supersedes(new TEXT, old TEXT);''')
    for e in events:
        db.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?,?)', tuple(e[k] for k in ['id','world','entity','key','value','authority','valid','observed']))
        db.executemany('INSERT INTO scope VALUES(?,?)', [(e['id'], s) for s in e['scopes']])
        db.executemany('INSERT INTO supersedes VALUES(?,?)', [(e['id'], s) for s in e['supersedes']])
    db.executemany('INSERT INTO permits VALUES(?)', [(s,) for s in q['scopes']])
    db.execute('''CREATE TEMP TABLE eligible AS SELECT * FROM events e WHERE world=? AND valid<=? AND observed<=?
      AND NOT EXISTS(SELECT 1 FROM scope s WHERE s.id=e.id AND NOT EXISTS
          (SELECT 1 FROM permits p WHERE p.permission=s.permission))''', (q['world'], q['valid_at'], q['known_at']))
    db.executescript('''CREATE TEMP TABLE current AS SELECT * FROM eligible e WHERE NOT EXISTS
      (SELECT 1 FROM supersedes s JOIN eligible n ON s.new=n.id WHERE s.old=e.id);
      CREATE TEMP TABLE unique_facts AS SELECT entity,key,authority,MIN(value) AS value
      FROM current GROUP BY entity,key,authority HAVING COUNT(DISTINCT value)=1;''')
    output = {}
    for t in catalog:
        if t['objective'] != q['objective'] or t['units'] > q['max_units']:
            continue
        joins, clauses, params = [], [], []
        for i, r in enumerate(t['requirements']):
            joins.append(f'unique_facts f{i}')
            clauses += [f'f{i}.entity=?', f'f{i}.key=?', f'f{i}.authority=?']
            params += [q['account'] if r['entity'] == '$account' else r['entity'], r['key'], r['authority']]
            if 'equals' in r:
                clauses.append(f'f{i}.value=?')
                params.append(r['equals'])
        clauses += [f'f{a}.value=f{b}.value' for a, b in t['equalities']]
        if db.execute('SELECT 1 FROM ' + ','.join(joins) + ' WHERE ' + ' AND '.join(clauses) + ' LIMIT 1', params).fetchone():
            output[t['id']]=[]
            if witnesses:
                for r in t['requirements']:
                    entity=q['account'] if r['entity']=='$account' else r['entity']
                    output[t['id']].append([row[0] for row in db.execute(
                        'SELECT id FROM current WHERE entity=? AND key=? AND authority=? ORDER BY id',
                        (entity,r['key'],r['authority']))])
    db.close()
    return output if witnesses else sorted(output)


def score(output, events, evidence, q, catalog, gold, slot_bindings=None):
    truth = applicable(visible(events, q), q, catalog)
    if sorted(truth) != sorted(gold):
        raise ValueError('gold disagrees with contract')
    result = dict(schema_valid=False, decision_correct=False, choice_correct=False,
                  recommended=False, supported_recommendation=False, inappropriate_abstention=False,
                  correct_withhold=False, violations=[], dry_run=None)
    if not isinstance(output, dict) or set(output) != {'status', 'plays', 'missing'}:
        result['violations'].append('schema'); return result
    if output['status'] not in ['recommend','request_evidence'] or not isinstance(output['plays'], list) or not isinstance(output['missing'], list) or not all(isinstance(s,str) for s in output['missing']):
        result['violations'].append('schema'); return result
    if len(output['plays']) > 1 or (output['status'] == 'recommend') != (len(output['plays']) == 1):
        result['violations'].append('status_or_play_limit'); return result
    for p in output['plays']:
        if not isinstance(p,dict) or set(p) != {'template','evidence'} or not isinstance(p['template'],str) or not isinstance(p['evidence'],list) or not all(isinstance(i,str) for i in p['evidence']) or len(p['evidence']) != len(set(p['evidence'])):
            result['violations'].append('play_schema'); return result
    result['schema_valid'] = True
    if not output['plays']:
        result['inappropriate_abstention'] = bool(truth)
        result['correct_withhold'] = not truth
        result['decision_correct'] = result['choice_correct'] = not truth
        return result
    result['recommended'] = True
    p = output['plays'][0]
    tid = p['template']
    result['choice_correct'] = tid in truth
    if tid not in truth:
        result['violations'].append('inapplicable_template')
    if slot_bindings is not None:
        template=next((t for t in catalog if t['id']==tid),None)
        byid={e['id']:e for e in evidence}
        if template is None or set(slot_bindings)!={slot_name(r) for r in template['requirements']}:
            result['violations'].append('binding_schema')
        else:
            for r in template['requirements']:
                eid=slot_bindings[slot_name(r)]
                if eid is None:continue
                e=byid.get(eid)
                entity=q['account'] if r['entity']=='$account' else r['entity']
                if e is None or (e['entity'],e['key'],e['authority'])!=(entity,r['key'],r['authority']):
                    result['violations'].append('misbound_support');break
    ids = set(p['evidence'])
    supplied = {e['id'] for e in evidence}
    current = {e['id'] for e in visible(events,q)}
    if not ids <= supplied:
        result['violations'].append('unsupplied_citation')
    if not ids <= current:
        result['violations'].append('obsolete_or_ineligible_citation')
    if tid in truth and any(not (ids & group) for group in truth[tid]):
        result['violations'].append('incomplete_support')
    # Extra citations are allowed only if relevant to at least one required slot.
    if tid in truth and not ids <= set.union(*truth[tid]):
        result['violations'].append('irrelevant_citation')
    result['decision_correct'] = result['supported_recommendation'] = not result['violations']
    if result['supported_recommendation']:
        t = next(t for t in catalog if t['id'] == tid)
        byid = {e['id']:e for e in events}
        result['dry_run'] = {'kind':'mock_catalog_validation', 'status':'executable',
            'account':q['account'], 'objective':q['objective'], 'template':tid,
            'policy_versions':sorted(i for i in ids if byid[i]['authority']=='approved'),
            'evidence':sorted(ids), 'units':t['units'], 'steps':t['workflow'],
            'mechanism_hypothesis':t['mechanism'], 'allowed_next_step':'dry_run'}
    return result
