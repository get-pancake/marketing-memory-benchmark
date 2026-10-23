"""Transparent task, temporal boundary, optimization and output scoring.

Retrieval imports no eligibility or optimization functions. Utility is a
constructed approved-policy priority, not a commercial reward model.
"""
from itertools import combinations
import hashlib,json

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def sha(x):return hashlib.sha256(x).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

CATALOG=[
 {'id':'diagnostic','cost':2,'multiplier':2,'signals':['risk','growth'],'extra':[]},
 {'id':'workshop','cost':3,'multiplier':4,'signals':['risk','launch'],'extra':['capacity']},
 {'id':'renewal_review','cost':2,'multiplier':3,'signals':['renewal'],'extra':[]},
 {'id':'reference_intro','cost':4,'multiplier':5,'signals':['growth','renewal'],'extra':['shareable']},
 {'id':'assurance_pack','cost':3,'multiplier':4,'signals':['risk'],'extra':['assurance']},
 {'id':'research_brief','cost':1,'multiplier':1,'signals':['risk','growth','renewal','launch'],'extra':[]},
]
CORE_RELATIONS={'policy','profile','consent','initiative','need','offering','proof','verified','signal','priority'}
EXTRA_RELATIONS={'capacity','shareable','assurance'}
SYSTEM='''You are a marketing decision-support analyst. Use only supplied current company evidence and the common action catalog. Select up to three actions for distinct accounts to maximize the SUM of approved priority times catalog multiplier under the query's shared cost budget. These policy points are synthetic priorities, NOT expected revenue. Check every action separately; do not let one ineligible account block another.
Eligibility for every action requires: seller policy is approved, the account profile region is allowed and sector not blocked, the action is approved by policy, current observed consent is true, and the signal matches the catalog. Follow account.initiative -> initiative.need -> need.offering -> offering.proof -> proof.verified; verified must be approved true. Account priority must be approved and an integer. Profile, consent, initiative, need, offering, proof and signal require observed authority. Additional capacity and assurance are approved true on the offering; shareable is approved true on the proof. The account itself must be in the query. Missing facts and conflicting current values at the required authority block the affected action. Proposed policies and feedback are not approved facts. Never assume a missing fact.
All supplied records have already passed the current-view filter. A later timestamp alone NEVER supersedes another supplied current record. If supplied values conflict at the required authority, abstain for that requirement even when one record has a later date.
For each chosen action cite ALL supplied source IDs required for its eligibility AND priority, including policy and every link in the chain. Do not cite unrelated records as proof. Distinct-account, cost and maximum-action constraints apply to the whole plan. When no supported action is available return an empty actions list and request missing evidence. Return the exact JSON schema, with a short reasoning summary and a missing-evidence list. Do not invent company facts or predicted conversion rates.'''

def visible(events,q):
    candidates=[e for e in events if e['valid_day']<=q['day'] and e['observed_day']<=q['day']
                and e['access'] in q['access']]
    # Supersession requires matching entity/relation/authority; a proposal cannot
    # silently retire approved policy, even if its source claims a replacement.
    byid={e['id']:e for e in candidates};retired=set()
    for e in candidates:
        for identity in e.get('supersedes',[]):
            old=byid.get(identity)
            if old and (old['entity'],old['relation'],old['authority'])==(e['entity'],e['relation'],e['authority']):retired.add(identity)
    return [e for e in candidates if e['id'] not in retired]

def index(events):
    out={}
    for e in events:out.setdefault((e['entity'],e['relation'],e['authority']),[]).append(e)
    return out

def read(idx,entity,relation,authority):
    rows=idx.get((entity,relation,authority),[])
    if not rows or len({canonical(r['value']) for r in rows})!=1:raise ValueError('missing or conflicting evidence')
    # All duplicate equivalent sources are acceptable evidence alternatives.
    return rows[0]['value'],{r['id'] for r in rows}

def candidates(events,q):
    idx=index(events);out=[]
    for account in q['accounts']:
        for t in CATALOG:
            groups=[]
            def get(entity,relation,authority='observed'):
                value,ids=read(idx,entity,relation,authority);groups.append(ids);return value
            try:
                policy=get('seller','policy','approved');profile=get(account,'profile')
                if profile['region'] not in policy['allowed_regions'] or profile['sector'] in policy['blocked_sectors'] or t['id'] not in policy['actions']:continue
                if get(account,'consent') is not True:continue
                if get(account,'signal') not in t['signals']:continue
                initiative=get(account,'initiative');need=get(initiative,'need');offering=get(need,'offering');proof=get(offering,'proof')
                if get(proof,'verified','approved') is not True:continue
                for extra in t['extra']:
                    if get(proof if extra=='shareable' else offering,extra,'approved') is not True:raise ValueError('unmet prerequisite')
                priority=get(account,'priority','approved')
                if type(priority) is not int or priority<0:continue
                out.append({'account':account,'action':t['id'],'cost':t['cost'],'value':priority*t['multiplier'],
                            'support_groups':[sorted(g) for g in groups]})
            except (ValueError,KeyError,TypeError):continue
    return out

def optimize(items,budget,max_actions=3):
    """Exact multiple-choice knapsack, one action at most per account."""
    groups={}
    for x in items:groups.setdefault(x['account'],[]).append(x)
    dp={(0,0):(0,[])}
    for account,opts in sorted(groups.items()):
        nxt=dict(dp)
        for (cost,count),(value,plan) in dp.items():
            for item in opts:
                key=(cost+item['cost'],count+1)
                if key[0]>budget or key[1]>max_actions:continue
                v=value+item['value']
                if v>nxt.get(key,(-1,[]))[0]:nxt[key]=(v,plan+[item])
        dp=nxt
    value,plan=max(dp.values(),key=lambda x:x[0]);return {'value':value,'plan':plan}

def enumerate_optimum(items,budget,max_actions=3):
    """Separate exhaustive reference, used only for oracle checks."""
    best=0
    for k in range(1,max_actions+1):
        for plan in combinations(items,k):
            if len({x['account'] for x in plan})==k and sum(x['cost'] for x in plan)<=budget:
                best=max(best,sum(x['value'] for x in plan))
    return best

def gold(case):
    items=candidates(visible(case['events'],case['query']),case['query'])
    opt=optimize(items,case['query']['budget'])
    return {'case_id':case['id'],'world':case['world'],'eligible':items,'optimum':opt['value'],'reference_plan':opt['plan']}

def score(raw,case,evidence):
    all_items=candidates(visible(case['events'],case['query']),case['query']);full=optimize(all_items,case['query']['budget'])['value']
    local_items=candidates(evidence,case['query']);recoverable=optimize(local_items,case['query']['budget'])['value']
    eligible={(x['account'],x['action']):x for x in all_items};supplied={e['id'] for e in evidence}
    actions=raw.get('actions',[]);errors=[];valid=[]
    if not isinstance(actions,list):actions=[];errors.append('malformed_actions')
    for action in actions:
        key=(action.get('account'),action.get('action'));item=eligible.get(key);citations=set(action.get('sources',[]))
        if item is None:errors.append('ineligible_action');continue
        if not citations<=supplied or not all(set(g)&citations for g in item['support_groups']):errors.append('unsupported_action');continue
        valid.append(item)
    if len(actions)>3:errors.append('too_many_actions')
    if len({a.get('account') for a in actions})!=len(actions):errors.append('duplicate_account')
    cost=sum(next((x['cost'] for x in CATALOG if x['id']==a.get('action')),0) for a in actions)
    if cost>case['query']['budget']:errors.append('over_budget')
    value=sum(x['value'] for x in valid) if not errors else 0
    return {'optimum':full,'recoverable_value':recoverable,'returned_value':value,
            'normalized_value':value/full if full else None,'context_normalized_value':recoverable/full if full else None,
            'feasible_grounded':not errors,'exact_optimum':not errors and value==full,
            'actionable':not errors and value>0,'abstained':not actions,'unsafe':bool(errors),
            'valid_action_count':len(valid),'actions_count':len(actions),'errors':errors,'cost_units':cost}

def source_view(e):
    return {k:e[k] for k in ['id','entity','relation','value','authority','valid_day','observed_day']}
def event_text(e):
    return canonical({k:e[k] for k in ['entity','relation','value','authority']})+' '+e.get('description','')
def query_text(q):
    return 'Marketing next best actions: '+q['objective']+' accounts '+', '.join(q['accounts'])+'; company policy, profile, consent, signal, initiative need offering proof verified, approved priority, capacity shareable assurance.'
def messages(q,records):
    return [{'role':'system','content':SYSTEM},{'role':'user','content':canonical({'query':q,'catalog':CATALOG,'company_evidence':[source_view(e) for e in records]})}]
def output_schema(q):
    return {'type':'object','properties':{
      'actions':{'type':'array','items':{'type':'object','properties':{'account':{'type':'string','enum':q['accounts']},'action':{'type':'string','enum':[t['id'] for t in CATALOG]},'sources':{'type':'array','items':{'type':'string'}}},'required':['account','action','sources'],'additionalProperties':False}},
      'reasoning_summary':{'type':'string'},'missing':{'type':'array','items':{'type':'string'}}},
      'required':['actions','reasoning_summary','missing'],'additionalProperties':False}
