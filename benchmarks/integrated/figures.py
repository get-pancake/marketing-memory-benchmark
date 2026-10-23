#!/usr/bin/env python3
"""Publication vector figures/tables derived exclusively from saved integrated results."""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from benchmarks.integrated.common import ARMS,sha

LABEL={'none':'No context','generic':'Generic hybrid','markdown':'Structured Markdown',
       'gbrain':'GBrain search','specialized':'Specialized coverage','gbrain_specialized':'GBrain + coverage','full':'Full current context'}
MODEL={'openai':'GPT-6.1 Sol','anthropic':'Claude Sonnet 5.5'}
COLORS=['#9ca3af','#3966a0','#8064a2','#c08235','#007f78','#438a4c','#343c47']

def generate(main,context,external,output,chunks=None):
    s=json.loads(main.read_text());e=json.loads(external.read_text())
    if chunks:e['groups'].update(json.loads(chunks.read_text())['groups'])
    if s['run_status']!='completed':raise ValueError('Incomplete main run; retain failures but do not silently omit unissued requests')
    rows=[json.loads(x) for x in context.read_text().splitlines()]
    output.mkdir(parents=True,exist_ok=True);saved=[]
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,
        'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'integrated-memory-v3','axes.titleweight':'bold'})
    def save(fig,name):
        fig.tight_layout()
        for suffix in ['pdf','svg']:
            path=output/(name+'.'+suffix)
            fig.savefig(path,bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None} if suffix=='pdf' else {'Date':None})
            saved.append(path)
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.3,2.7));ax.set(xlim=(-.15,10.15),ylim=(0,4));ax.axis('off')
    boxes=[(.0,1.1,2.0,1.7,'Same company records\nCurrent + permitted\nShared action catalog'),
           (2.8,.25,2.3,3.25,'Context intervention\n\nNone / Generic hybrid\nStructured Markdown\nGBrain / Specialized\nGBrain + coverage / Full'),
           (5.9,2.1,1.8,1.1,'Fixed GPT reader\nSame prompt/settings'),
           (5.9,.5,1.8,1.1,'Fixed Claude reader\nSame prompt/settings'),
           (8.35,.6,1.65,2.5,'Two outcomes\n\nComplete evidence\nGrounded action\n\nTokens + cost')]
    for x,y,w,h,t in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.03',facecolor='#f2f5f7',edgecolor='#526273'))
        ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=8)
    for a,b in [((2,2),(2.75,2)),((5.15,2.5),(5.85,2.65)),((5.15,1.3),(5.85,1.05)),((7.75,2.65),(8.3,2.3)),((7.75,1.05),(8.3,1.4))]:
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,color='#526273'))
    save(fig,'design')
    budgets=sorted({r['budget_bytes'] for r in rows});matrix=[];denom=None
    for arm in ARMS:
        values=[]
        for cap in budgets:
            rs=[r for r in rows if r['arm']==arm and r['budget_bytes']==cap and r['context']['answerable']]
            denom=len(rs);values.append(sum(r['context']['complete_positive_support'] for r in rs))
        matrix.append(values)
    path=output/'context-summary.json'
    path.write_text(json.dumps({'source_sha256':sha(context.read_bytes()),'positive_cases':denom,
        'budgets_bytes':budgets,'complete_support':{
            arm:{str(cap):matrix[i][j] for j,cap in enumerate(budgets)}
            for i,arm in enumerate(ARMS)},
        'scope':'Retrieval-only budget sweep. Reader calls use 2048 bytes; Full is exempt.'},indent=2)+'\n')
    saved.append(path)
    derived={}
    for provider in MODEL:
        generic=s['groups'][provider+'/generic'];special=s['groups'][provider+'/specialized'];full=s['groups'][provider+'/full']
        derived[provider]={
            'generic_correct_percent':100*generic['correct']/generic['cases'],
            'specialized_correct_percent':100*special['correct']/special['cases'],
            'correct_difference_percentage_points':100*(special['correct']-generic['correct'])/generic['cases'],
            'additional_supported_recommendations':special['supported']-generic['supported'],
            'relative_supported_increase_percent':100*(special['supported']/generic['supported']-1),
            'positive_coverage_difference_percentage_points':100*(special['supported']-generic['supported'])/generic['positive_cases'],
            'input_reduction_vs_full_percent':100*(1-special['mean_input_tokens']/full['mean_input_tokens'])}
    path=output/'report-metrics.json'
    path.write_text(json.dumps({'input_summary_semantic_sha256':sha(json.dumps({k:v for k,v in s.items() if k!='created_at'},sort_keys=True).encode()),'derived':derived,
        'interpretation':'Percentages are formal fixture outcomes/input reductions, not commercial utility or total-cost reductions.'},indent=2)+'\n')
    saved.append(path)
    fig,ax=plt.subplots(figsize=(7.3,3.1))
    im=ax.imshow(np.array(matrix)/denom,vmin=0,vmax=1,cmap='Blues',aspect='auto')
    for i,vals in enumerate(matrix):
        for j,n in enumerate(vals):ax.text(j,i,f'{n}/{denom}',ha='center',va='center',color='white' if n/denom>.6 else '#152335')
    ax.set(yticks=range(7),yticklabels=[LABEL[a] for a in ARMS],xticks=range(4),xticklabels=[f'{b:,}' for b in budgets],xlabel='Evidence budget (UTF-8 bytes; Full is exempt)')
    ax.set_title('Complete current support on answerable cases',loc='left',fontsize=10)
    fig.colorbar(im,ax=ax,shrink=.8,label='Fraction with complete support')
    save(fig,'retrieval-budget')
    fig,axes=plt.subplots(1,2,figsize=(7.3,3.6),sharey=True)
    for ax,(provider,title) in zip(axes,MODEL.items()):
        for i,arm in enumerate(ARMS):
            g=s['groups'][provider+'/'+arm];y=6-i;v=g['correct_rate']*100;ci=np.array(g['correct_world_ci95'])*100
            ax.barh(y,v,height=.55,color=COLORS[i],alpha=.9)
            ax.plot(ci,[y,y],color='#152335',linewidth=1.5)
            ax.text(101,y,f"{g['correct']}/{g['cases']}",va='center',fontsize=8)
        ax.set(xlim=(0,119),xticks=[0,25,50,75,100],yticks=range(7),yticklabels=[LABEL[a] for a in reversed(ARMS)],xlabel='Grounded correct decisions (%)')
        ax.set_title(title,fontsize=10);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    save(fig,'reader-quality')
    comparisons=['generic','markdown','gbrain','gbrain_specialized','full']
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.8),sharey=True)
    upper=max(v['ci95'][1] for k,v in s['contrasts'].items() if not k.endswith('none'))*100
    for ax,(provider,title) in zip(axes,MODEL.items()):
        ax.axvline(0,color='#9ca3af',linewidth=1)
        for i,arm in enumerate(comparisons):
            g=s['contrasts'][provider+'/specialized-minus-'+arm];y=4-i;color='#007f78' if arm=='generic' else '#526273'
            ax.plot(np.array(g['ci95'])*100,[y,y],color=color,linewidth=2)
            ax.plot(g['difference']*100,y,'o',color=color,markersize=5)
        ax.set(yticks=range(5),yticklabels=['vs '+LABEL[a] for a in reversed(comparisons)],xlim=(-5,upper+5),xlabel='Improvement (percentage points)')
        ax.set_title(title,fontsize=10);ax.grid(axis='x',alpha=.15)
    save(fig,'paired-effects')
    fig,axes=plt.subplots(1,2,figsize=(7.3,3.5),sharey=True)
    names=['Supported recommendation','Correct withholding','Inappropriate abstention','Other error / failure']
    colors=['#007f78','#90c6bd','#dba74c','#b84a53']
    for ax,(provider,title) in zip(axes,MODEL.items()):
        values=[]
        for arm in ARMS:
            g=s['groups'][provider+'/'+arm];v=[g['supported'],g['correct_withhold'],g['inappropriate_abstentions']]
            values.append(v+[g['cases']-sum(v)])
        left=np.zeros(7)
        for j,name in enumerate(names):
            vals=np.array([v[j] for v in values])/s['groups'][provider+'/none']['cases']*100
            ax.barh(np.arange(7)[::-1],vals,left=left,color=colors[j],height=.6,label=name);left+=vals
        ax.set(yticks=range(7),yticklabels=[LABEL[a] for a in reversed(ARMS)],xlim=(0,100),xlabel='Share of all cases (%)');ax.set_title(title,fontsize=10)
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2,bbox_to_anchor=(.5,-.11),frameon=False,fontsize=8)
    save(fig,'decision-composition')
    exarms=['none','raw_bm25','raw_full','wiki_generic','wiki_specialized']
    exlabels=['No context','Raw BM25','Raw full','Generic wiki','Marketing wiki']
    if chunks:
        exarms.insert(2,'raw_chunks');exlabels.insert(2,'Chunked BM25*')
    fig,ax=plt.subplots(figsize=(7.3,1.9))
    vals=np.array([[e['groups'][p+'/'+a]['correct'] for a in exarms] for p in MODEL])
    im=ax.imshow(vals/22,vmin=0,vmax=1,cmap='Blues',aspect='auto')
    for i in range(2):
        for j in range(len(exarms)):ax.text(j,i,f'{vals[i,j]}/22',ha='center',va='center',color='white' if vals[i,j]/22>.6 else '#152335')
    ax.set(yticks=[0,1],yticklabels=list(MODEL.values()),xticks=range(len(exarms)),xticklabels=exlabels)
    ax.set_title('External development QA: exact answer correctness',loc='left',fontsize=10)
    save(fig,'external-qa')
    lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Context & Complete support & GPT correct & Claude correct \\',r'\midrule']
    for arm in ARMS:
        a,b=[s['groups'][p+'/'+arm] for p in MODEL]
        lines.append(f"{LABEL[arm]} & {a['complete_support']}/{a['positive_cases']} & {a['correct']}/{a['cases']} & {b['correct']}/{b['cases']} \\\\")
    lines += [r'\bottomrule',r'\end{tabular}'];path=output/'results-table.tex';path.write_text('\n'.join(lines)+'\n');saved.append(path)
    lines=[r'\begin{tabular}{llrrrr}',r'\toprule',r'Reader & Context & Input & Output & \$/100 calls & Seconds \\',r'\midrule']
    for provider,title in MODEL.items():
        for arm in ARMS:
            g=s['groups'][provider+'/'+arm]
            lines.append(f"{title if arm=='none' else ''} & {LABEL[arm]} & {g['mean_input_tokens']:.0f} & {g['output_tokens']/g['cases']:.0f} & {100*g['estimated_usd']/g['cases']:.3f} & {g['mean_seconds']:.2f} \\\\")
        lines.append(r'\midrule')
    lines[-1]=r'\bottomrule';lines.append(r'\end{tabular}')
    path=output/'resource-table.tex';path.write_text('\n'.join(lines)+'\n');saved.append(path)
    numbers={'MainWorlds':str(s['worlds']),'MainCases':str(s['groups']['openai/none']['cases']),
             'MainCalls':f"{s['planned_calls']:,}".replace(',',r'\,'),
             'MainPositives':str(s['groups']['openai/none']['positive_cases']),
             'CompleteGeneric':str(s['groups']['openai/generic']['complete_support']),
             'CompleteSpecial':str(s['groups']['openai/specialized']['complete_support']),
             'MainCost':f"{s['cost_estimate_usd']:.2f}"}
    for provider,prefix in [('openai','Gpt'),('anthropic','Claude')]:
        c=s['contrasts'][provider+'/specialized-minus-generic']
        numbers.update({prefix+'SpecialCorrect':str(s['groups'][provider+'/specialized']['correct']),
                        prefix+'GenericCorrect':str(s['groups'][provider+'/generic']['correct']),
                        prefix+'Difference':f"{100*c['difference']:.1f}",
                        prefix+'Low':f"{100*c['ci95'][0]:.1f}",prefix+'High':f"{100*c['ci95'][1]:.1f}"})
    path=output/'numbers.tex';path.write_text(''.join('\\newcommand{\\'+key+'}{'+value+'}\n' for key,value in numbers.items()));saved.append(path)
    manifest={'source_sha256':{str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name:sha(p.read_bytes()) for p in [main,context,external]+([chunks] if chunks else [])},
              'figure_source_sha256':sha(Path(__file__).read_bytes()),'files':{p.name:sha(p.read_bytes()) for p in saved}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'figures':6,'files':len(saved)}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['main','context','external','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--chunks',type=Path)
    a=p.parse_args();generate(a.main,a.context,a.external,a.output,a.chunks)
