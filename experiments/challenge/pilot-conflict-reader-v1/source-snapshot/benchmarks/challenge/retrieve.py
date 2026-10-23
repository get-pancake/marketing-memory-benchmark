"""Label-blind packing: native ranks, entity closure, or catalog-typed closure.

No eligibility, consent-value, priority-value or utility calculation is used.
All current conflicting/approval variants of a selected slot travel together.
"""
import math,re
from collections import Counter,deque
from benchmarks.challenge.core import canonical,source_view,event_text,CORE_RELATIONS,EXTRA_RELATIONS

ARMS=['none','company','gtm','markdown','gbrain','full']
LABELS={'none':'No company context','company':'Company context','gtm':'GTM context',
        'markdown':'Markdown + entity closure','gbrain':'GBrain search','full':'Full current context'}
def pack(events,ordered,cap):
    byid={e['id']:e for e in events};chosen=[];seen=set();used=2
    # Slot bundles preserve contradictions and duplicate authoritative records.
    slots={}
    for e in events:slots.setdefault((e['entity'],e['relation']),[]).append(e)
    for identity in ordered:
        row=byid[identity]
        bundle=sorted(slots[(row['entity'],row['relation'])],key=lambda e:e['id'])
        bundle=[e for e in bundle if e['id'] not in seen]
        size=sum(len(canonical(source_view(e)).encode())+1 for e in bundle)
        if used+size>cap:continue
        chosen.extend(bundle);seen.update(e['id'] for e in bundle);used+=size
    return chosen

def closure(events,anchor,typed):
    byentity={}
    for e in events:byentity.setdefault(e['entity'],[]).append(e)
    frontier=deque([(anchor,0)]);seen=set();rows=[]
    while frontier:
        entity,depth=frontier.popleft()
        if entity in seen:continue
        seen.add(entity)
        for row in sorted(byentity.get(entity,[]),key=lambda r:r['id']):
            if typed and row['relation'] not in CORE_RELATIONS|EXTRA_RELATIONS:continue
            rows.append(row)
            value=row['value']
            if depth<4 and isinstance(value,str) and value in byentity:frontier.append((value,depth+1))
    return rows

def select(events,q,ranks,arm,cap):
    if arm=='none':return []
    if arm=='full':return sorted(events,key=lambda e:e['id'])
    ranks=list(dict.fromkeys(ranks+[e['id'] for e in sorted(events,key=lambda e:e['id'])]))
    if arm=='gbrain':return pack(events,ranks,cap)
    pos={identity:i for i,identity in enumerate(ranks)}
    # Company policy is explicitly requested by the shared task, supplied to
    # both closure methods without choosing which policy value is favorable.
    policy=[e for e in events if e['entity']=='seller' and e['relation']=='policy']
    account_order=sorted(q['accounts'],key=lambda a:min((pos[e['id']] for e in events if e['entity']==a),default=len(pos)))
    ordered=[e['id'] for e in sorted(policy,key=lambda e:pos[e['id']])]
    for account in account_order:
        bundle=closure(events,account,typed=arm=='gtm')
        # Breadth of an entity bundle is preserved; source IDs order equal
        # graph depths deterministically, never by truth value/priority points.
        ordered.extend(e['id'] for e in bundle)
    ordered.extend(ranks)
    return pack(events,ordered,cap)

def rank_hybrid(events,query,vectors,query_vector):
    tokens=lambda s:re.findall(r'[a-z0-9_]+',s.lower())
    docs=[tokens(event_text(e)) for e in events];qt=set(tokens(query));df=Counter(t for d in docs for t in set(d));n=len(docs);avg=sum(map(len,docs))/max(n,1)
    sparse=[];dense=[]
    for i,(e,d) in enumerate(zip(events,docs)):
        counts=Counter(d);bm=0
        for t in qt:
            tf=counts[t]
            if tf:bm+=math.log(1+(n-df[t]+.5)/(df[t]+.5))*tf*2.2/(tf+1.2*(.25+.75*len(d)/avg))
        sparse.append((bm,e['id']));dense.append((sum(a*b for a,b in zip(vectors[e['id']],query_vector)),e['id']))
    sr={identity:i for i,(_,identity) in enumerate(sorted(sparse,key=lambda x:(-x[0],x[1])))}
    dr={identity:i for i,(_,identity) in enumerate(sorted(dense,key=lambda x:(-x[0],x[1])))}
    return sorted(sr,key=lambda identity:(-(1/(60+sr[identity])+1/(60+dr[identity])),identity))
