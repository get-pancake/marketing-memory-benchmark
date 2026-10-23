"""Supplementary provenance, prompt-control and difficulty audit; no API calls."""
import argparse,json,sys,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import canonical,sha,dump,visible,messages,source_view
from benchmarks.challenge.prompt_control import query_word_context

def audit(data,packets,output):
    idx=json.loads((data/'index.json').read_text());rows=[];levels={}
    for entry in idx['cases']:
        path=data/entry['path']
        if sha(path.read_bytes())!=entry['sha256']:raise ValueError('case hash differs')
        case=json.loads(path.read_text());ev=visible(case['events'],case['query']);allowed={e['id']:e for e in ev}
        receipt=json.loads((packets/case['id']/'receipt.json').read_text());ps=json.loads((packets/case['id']/'packets.json').read_text())
        for packet in ps:
            if not set(packet['evidence_ids'])<=set(allowed):raise ValueError('temporal/access leak')
            selected=[allowed[x] for x in packet['evidence_ids']]
            if messages(case['query'],selected)!=packet['messages']:raise ValueError('model messages differ from declared sources')
            size=len(canonical([source_view(e) for e in selected]).encode())
            if size!=packet['evidence_bytes'] or packet['arm']!='full' and size>case['budget_bytes']:raise ValueError('evidence accounting differs')
        gtm=next(p for p in ps if p['arm']=='gtm');control=query_word_context(ev,case['query'],receipt['gbrain_ranking'],case['budget_bytes'])
        equal=messages(case['query'],control)==gtm['messages']
        row={'case_id':case['id'],'world':case['world'],'level':case['level'],'records':len(ev),'all_records':len(case['events']),'accounts':len(case['query']['accounts']),
             'full_evidence_bytes':next(p['evidence_bytes'] for p in ps if p['arm']=='full'),'budget_bytes':case['budget_bytes'],
             'query_word_control_exact_input_equal':equal,'gtm_packet_sha256':sha(canonical(gtm['messages']).encode()),'query_word_packet_sha256':sha(canonical(messages(case['query'],control)).encode())}
        rows.append(row);levels.setdefault(case['level'],[]).append(row)
    result={'status':'passed','cases':len(rows),'packets_verified':len(rows)*6,'query_word_exact_equal_cases':sum(r['query_word_control_exact_input_equal'] for r in rows),'query_word_extra_model_calls':0,
            'independent_control_observations':0,'control_interpretation':'When exact inputs match, this is a mechanistic alias; no new observations and no measured architectural superiority over the generic task-word selector.',
            'levels':{level:{k:{'min':min(r[k] for r in rs),'median':statistics.median(r[k] for r in rs),'max':max(r[k] for r in rs)} for k in ['records','all_records','accounts','full_evidence_bytes','budget_bytes']} for level,rs in levels.items()},'rows':rows}
    if result['query_word_exact_equal_cases']!=result['cases']:raise ValueError('Distinct generic control packets require actual new reader calls; do not alias them')
    dump(output,result);print(canonical({k:result[k] for k in ['status','cases','packets_verified','query_word_exact_equal_cases']}))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--packets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.data,a.packets,a.output)
