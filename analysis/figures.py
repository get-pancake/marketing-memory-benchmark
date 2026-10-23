#!/usr/bin/env python3
"""Generate vector figures and a results table from saved, complete main analysis."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

LABELS={'generic_hybrid':'Generic hybrid','prompt_hybrid':'Prompt hybrid','facet_hybrid':'Facet hybrid',
        'typed':'Catalog coverage','full_context':'Full context','typed_history':'History ablation'}
COLORS=dict(zip(LABELS,['#6c757d','#3f6b98','#8a5e97','#007f79','#c37829','#a94644']))


def generate(summary_path, output, allow_pilot=False):
    summary=json.loads(summary_path.read_text())
    if not summary['source_run_complete']:raise ValueError('Incomplete run cannot generate final figures')
    manifest=json.loads((ROOT/summary['run']/'manifest.json').read_text())
    if manifest['dataset_manifest']['split']!='test' and not allow_pilot:
        raise ValueError('Pilot figure requires explicit --allow-pilot and is not a main result')
    output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                         'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'gtm-memory-v1','axes.titleweight':'bold'})
    methods=[m for m in LABELS if m in summary['methods']]
    stats=[summary['methods'][m] for m in methods]
    saved=[]
    def save(fig,name):
        fig.tight_layout()
        for suffix in ['pdf','svg']:
            path=output/(name+'.'+suffix)
            metadata={'CreationDate':None,'ModDate':None} if suffix=='pdf' else {'Date':None}
            fig.savefig(path,bbox_inches='tight',metadata=metadata);saved.append(path)
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7.3,3.5),sharey=True)
    for i,(m,s) in enumerate(zip(methods,stats)):
        y=len(methods)-i-1;value=s['primary']*100;ci=s['primary_world_ci95']
        axes[0].plot(value,y,'o',color=COLORS[m],markersize=6)
        if ci:axes[0].plot([ci[0]*100,ci[1]*100],[y,y],color=COLORS[m],linewidth=2)
        axes[1].plot(s['positive_support_available']*100,y,'s',mfc='white',mec=COLORS[m],ms=7)
        axes[1].plot(s['supported_positive_coverage']*100,y,'o',color=COLORS[m],ms=6)
    axes[0].set_yticks(range(len(methods)),[LABELS[m] for m in reversed(methods)])
    baseline=100*stats[0]['negative_cases']/stats[0]['planned']
    axes[0].axvline(baseline,linestyle=':',color='.65',label='Always withhold')
    axes[0].set_xlabel('Correct supported decision (%)')
    axes[0].set_title('All planned queries')
    axes[1].set_xlabel('Coverage on positive cases (%)')
    axes[1].set_title('Available support vs. used support')
    axes[1].plot([],[],'s',mfc='white',mec='.3',label='Complete support retrieved')
    axes[1].plot([],[],'o',color='.3',label='Supported recommendation')
    axes[1].legend(loc='upper center',bbox_to_anchor=(.5,-.18),fontsize=7,frameon=False)
    for ax in axes:ax.set_xlim(-3,103);ax.grid(axis='x',alpha=.15)
    save(fig,'quality')
    condition_order=['initial','weak_feedback','policy_revision','account_requalified',
                'evidence_correction','restricted_evidence','objective_change','policy_conflict']
    conditions=[c for c in condition_order if c in stats[0]['by_condition']]
    conditions+=sorted(set(stats[0]['by_condition'])-set(conditions))
    matrix=np.array([[s['by_condition'][c]['correct']/s['by_condition'][c]['n'] for c in conditions] for s in stats])
    fig,ax=plt.subplots(figsize=(7.5,3.4));plot=ax.imshow(matrix,vmin=0,vmax=1,cmap='Blues',aspect='auto')
    ax.set_yticks(range(len(methods)),[LABELS[m] for m in methods])
    ax.set_xticks(range(len(conditions)),[c.replace('_','\n') for c in conditions],fontsize=7)
    for i in range(len(methods)):
        for j in range(len(conditions)):
            cell=stats[i]['by_condition'][conditions[j]]
            ax.text(j,i,f"{cell['correct']}/{cell['n']}",ha='center',va='center',fontsize=8,color='white' if matrix[i,j]>.6 else 'black')
    fig.colorbar(plot,ax=ax,label='Supported-decision accuracy',shrink=.8)
    save(fig,'conditions')
    fig,ax=plt.subplots(figsize=(5.5,3.1))
    for i,(m,s) in enumerate(zip(methods,stats)):
        x=s['generation_p50_seconds'];y=s['primary']*100
        ax.scatter(x,y,color=COLORS[m],s=40,label=LABELS[m])
    ax.set_xlabel('Median generation request time (seconds)');ax.set_ylabel('Correct supported decision (%)')
    ax.set_ylim(-3,103);ax.grid(alpha=.15)
    ax.legend(fontsize=7,frameon=False,loc='upper left',bbox_to_anchor=(1.02,1))
    save(fig,'quality-cost')
    lines=[r'\begin{tabular}{lrrrrr}',r'\toprule',
           r'Method & Decision & Positive & Neg. rec. & Tokens & Gen. sec. \\',r'\midrule']
    percent=lambda value:'--' if value is None else f'{value*100:.1f}\\%'
    for m,s in zip(methods,stats):
        lines.append(f"{LABELS[m]} & {percent(s['primary'])} & {percent(s['supported_positive_coverage'])} & {percent(s['negative_recommendations'])} & {s['input_tokens']/s['planned']:.0f} & {s['generation_p50_seconds']:.1f} \\\\")
    lines.extend([r'\bottomrule',r'\end{tabular}'])
    table=output/'results-table.tex';table.write_text('\n'.join(lines)+'\n');saved.append(table)
    receipt=dict(source_analysis=str(summary_path),source_sha256=hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        matplotlib=matplotlib.__version__,numpy=np.__version__,pilot=manifest['dataset_manifest']['split']!='test',
        files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in saved})
    (output/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analysis',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--allow-pilot',action='store_true')
    a=p.parse_args();generate(a.analysis,a.output,a.allow_pilot)
