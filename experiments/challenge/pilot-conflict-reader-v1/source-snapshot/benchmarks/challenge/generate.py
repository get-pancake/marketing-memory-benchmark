"""Original fictional histories; generation and gold export are separate stages."""
import argparse,random,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.challenge.core import *

FAMILIES=['enterprise_software','industrial_services','professional_services']
LEVELS=[('accessible',4,64,16384),('constrained',6,128,12288),('stress',8,256,8192)]

def make_case(seed,wi,li):
    rng=random.Random(f'{seed}:{wi}');variant=random.Random(f'{seed}:{wi}:{li}:variant');world=f'w{seed}-{wi:03d}';level,n,noise,cap=LEVELS[li];cid=world+'-'+level
    events=[];seq=0
    def add(entity,relation,value,authority='observed',day=5,observed=None,access='public',supersedes=None,description=''):
        nonlocal seq
        seq+=1;identity='e'+sha(f'{cid}:{seq}'.encode())[:14]
        e=dict(id=identity,entity=entity,relation=relation,value=value,authority=authority,valid_day=day,observed_day=observed if observed is not None else day,access=access,supersedes=supersedes or [],description=description)
        events.append(e);return e
    names=rng.sample(['Aster','Birch','Cedar','Delta','Elm','Flint','Grove','Harbor','Iris','Juniper','Kestrel','Larch','Mesa','North','Orchid','Pine'],8)
    all_accounts=[name+'-'+str(wi) for name in names];accounts=all_accounts[:n]
    policy={'allowed_regions':rng.sample(['US','UK','DE','FR'],3),'blocked_sectors':['restricted'],'actions':[x['id'] for x in CATALOG]}
    old=add('seller','policy',dict(policy,allowed_regions=['US','UK','DE','FR']),'approved',day=1)
    add('seller','policy',policy,'approved',day=12,supersedes=[old['id']])
    add('seller','policy',dict(policy,allowed_regions=[]),'proposed',day=25,description='Unapproved suggestion; does not change policy.')
    all_negative=(wi+li)%5==0
    for ai,account in enumerate(all_accounts):
        init='initiative-'+str(ai);need='need-'+str(ai);offering='offering-'+str(ai);proof='proof-'+str(ai)
        region=rng.choice(['US','UK','DE','FR']);sector=rng.choice(['software','services','manufacturing','restricted'])
        # The first account is eligible in positive fixtures; other accounts are
        # independently varied. Labels are never supplied to retrieval/readers.
        if ai==0:region=policy['allowed_regions'][0];sector='services'
        add(account,'profile',{'region':region,'sector':sector})
        consent=not all_negative and (ai==0 or rng.random()>.18)
        base=add(account,'consent',True,day=2)
        add(account,'consent',consent,day=15,supersedes=[base['id']])
        add(account,'initiative',init)
        add(account,'signal',rng.choice(['risk','growth','renewal','launch']))
        add(account,'priority',rng.randint(1,12),'approved')
        add(init,'need',need);add(need,'offering',offering);add(offering,'proof',proof)
        add(proof,'verified',ai==0 or rng.random()>.15,'approved')
        add(offering,'capacity',rng.random()>.25,'approved')
        add(proof,'shareable',rng.random()>.3,'approved')
        add(offering,'assurance',rng.random()>.2,'approved')
        # Feedback must not be promoted into policy or inferred consent.
        add(account,'nonresponse',True,'feedback',description='No reply observed; no causal inference or approval.')
        # Current source conflicts affect some non-anchor candidates only.
        if ai>0 and li>0 and variant.random()<.18:add(account,'consent',not consent,day=24)
        # Corrections not yet observed and inaccessible notes cannot leak.
        add(account,'priority',1000,'approved',day=10,observed=40)
        add(account,'consent',True,day=28,access='restricted')
    # Company-domain distractors, including structurally linked but irrelevant
    # corporate records. A few legal/operations relations above ARE necessary.
    rng=variant
    nouns=['invoice','support_ticket','design_review','hiring_plan','budget_note','incident','supplier','meeting','brand_history','office_lease']
    for j in range(noise):
        anchor=rng.choice(accounts+['seller']+[f'initiative-{i}' for i in range(n)]+[f'offering-{i}' for i in range(n)])
        relation=rng.choice(nouns);entity='corporate-'+str(j)
        add(anchor,relation,entity,description='Company record linked to this account or project.')
        if j%3==0:
            add(entity,'summary',rng.choice(['Marketing account review has no approved targeting change.','Support observation, not customer permission.','Finance forecast is not an approved action priority.','Engineering log with no proof approval.']),authority='observed')
    rng.shuffle(events)
    q={'day':30,'access':['public'],'accounts':accounts,'budget':6+li,'objective':'Maximize approved marketing priority within the shared cost allowance; each account at most once.'}
    return {'id':cid,'world':world,'family':FAMILIES[wi%3],'level':level,'budget_bytes':cap,'query':q,'events':events}

def build(output,n,seed,split):
    output.mkdir(parents=True,exist_ok=False);entries=[]
    for wi in range(n):
        for li in range(3):
            case=make_case(seed,wi,li);path=output/'cases'/(case['id']+'.json');dump(path,case)
            entries.append({'id':case['id'],'world':case['world'],'family':case['family'],'level':case['level'],'path':str(path.relative_to(output)),'sha256':sha(path.read_bytes())})
    dump(output/'index.json',{'schema':1,'split':split,'seed':seed,'worlds':n,'cases':entries,'provenance':'Original generated fictional structured sources; not customer data. Independent implementation checks are not independent authorship.','license':'CC-BY-4.0'})
    # Hidden labels live in a separate directory never opened by preparation.
    for e in entries:
        case=json.loads((output/e['path']).read_text());dump(output/'labels'/(e['id']+'.json'),gold(case))
    print(canonical({'worlds':n,'cases':len(entries),'output':str(output)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worlds',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--split',required=True);a=p.parse_args();build(a.output,a.worlds,a.seed,a.split)
