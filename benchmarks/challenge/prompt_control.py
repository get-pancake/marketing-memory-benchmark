"""Generic query-word closure control, without a GTM relation allowlist.

If this reconstructs the exact GTM packet, an additional model call would be a
replicate of an identical input, not evidence for an architectural difference.
"""
import re
from benchmarks.challenge.core import query_text
from benchmarks.challenge.retrieve import closure,pack

def query_word_context(events,q,ranks,cap):
    words=set(re.findall(r'[a-z0-9_]+',query_text(q).lower()))
    filtered=[e for e in events if e['relation'].lower() in words]
    ranks=list(dict.fromkeys(ranks+[e['id'] for e in sorted(events,key=lambda e:e['id'])]));pos={x:i for i,x in enumerate(ranks)}
    policy=[e for e in events if e['entity']=='seller' and e['relation']=='policy']
    order=sorted(q['accounts'],key=lambda a:min((pos[e['id']] for e in events if e['entity']==a),default=len(pos)))
    ids=[e['id'] for e in sorted(policy,key=lambda e:pos[e['id']])]
    for a in order:ids.extend(e['id'] for e in closure(filtered,a,False))
    ids.extend(ranks)
    return pack(events,ids,cap)
