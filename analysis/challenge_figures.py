"""Publication figures and tables generated solely from saved challenge analysis."""
import argparse,json,sys,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/marketing-research-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/marketing-research-font-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import dump,sha
from benchmarks.challenge.retrieve import ARMS,LABELS

COLORS={'none':'#828995','company':'#3674B5','gtm':'#D5602D','markdown':'#6B8E70','gbrain':'#A69C86','full':'#3D3D3D'}
SHORT={'none':'No\ncontext','company':'Company\ncontext','gtm':'GTM\ncontext','markdown':'Markdown + closure','gbrain':'GBrain search','full':'Full current context'}
MODELS={'openai':'GPT-6.1 Sol','anthropic':'Opus 5.5'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','svg.hashsalt':'marketing-challenge-v4','pdf.fonttype':42,'ps.fonttype':42})

def save(fig,out,name):
    fig.savefig(out/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)
def grid(ax):ax.set_axisbelow(True);ax.grid(axis='y',alpha=.18);ax.set_ylim(0,105)

def main():
    p=argparse.ArgumentParser();p.add_argument('--summary',type=Path,required=True);p.add_argument('--budget',type=Path);p.add_argument('--external',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    s=json.loads(a.summary.read_text());a.output.mkdir(parents=True,exist_ok=True);idx={(x['provider'],x['arm']):x for x in s['summary']};mainarms=['none','company','gtm']
    fig,axs=plt.subplots(1,3,figsize=(7.2,2.8),sharey=True)
    for j,(ax,title) in enumerate(zip(axs,['Evidence available',MODELS['openai'],MODELS['anthropic']])):
        for i,arm in enumerate(mainarms):
            r=idx[('openai' if j<2 else 'anthropic',arm)];v=100*(r['context_value'] if j==0 else r['mean_normalized_value'])
            err=None if j==0 else [[v-r['ci95'][0]*100],[r['ci95'][1]*100-v]]
            ax.bar(i,v,color=COLORS[arm],width=.62,yerr=err,capsize=4,error_kw={'lw':1})
            label_y=(v if j==0 else r['ci95'][1]*100)+4
            ax.text(i,label_y,f'{v:.1f}%',ha='center',fontweight='bold',fontsize=9)
        ax.set_xticks(range(3),[SHORT[x] for x in mainarms]);ax.set_title(title);grid(ax);ax.set_ylim(0,112)
    axs[0].set_ylabel('Normalized policy value (%)')
    fig.tight_layout();save(fig,a.output,'headline')
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.3),sharey=True)
    levels=['accessible','constrained','stress']
    for ax,provider in zip(axs,MODELS):
        for arm in mainarms+['full']:
            r=idx[(provider,arm)];ys=[r['by_level'][l]['mean_normalized_value']*100 for l in levels]
            ax.plot(range(3),ys,marker='o',color=COLORS[arm],label=LABELS[arm],lw=2,ls='--' if arm=='full' else '-')
        ax.set_xticks(range(3),['4 accounts\n16 KiB','6 accounts\n12 KiB','8 accounts\n8 KiB']);ax.set_title(MODELS[provider]);grid(ax)
    fig.supxlabel('Compound stress level: more accounts and distractors, less evidence',fontsize=9)
    axs[0].set_ylabel('Grounded policy value (%)');axs[1].legend(fontsize=8,loc='lower left',framealpha=.9)
    fig.tight_layout();save(fig,a.output,'difficulty')
    order=['none','gbrain','company','markdown','gtm','full'];table=[]
    for arm in order:table.append([idx[('openai',arm)]['context_value']*100]+[idx[(p,arm)]['mean_normalized_value']*100 for p in MODELS])
    # Mechanistic prompt-derived control aliases an identical packet; do not
    # count it as another independently executed generation arm.
    table.insert(5,table[4].copy());names=[LABELS[x] for x in order];names.insert(5,'Company + query words*')
    fig,ax=plt.subplots(figsize=(7.2,3.9));im=ax.imshow(table,vmin=0,vmax=100,cmap='Blues',aspect='auto')
    for i,row in enumerate(table):
        for j,v in enumerate(row):ax.text(j,i,f'{v:.1f}%',ha='center',va='center',color='white' if v>58 else '#122033',fontweight='bold')
    ax.set_yticks(range(len(names)),names);ax.set_xticks(range(3),['Evidence available',MODELS['openai'],MODELS['anthropic']]);ax.xaxis.tick_top()
    fig.colorbar(im,ax=ax,label='Normalized policy value (%)',fraction=.04,pad=.04)
    fig.text(.01,.005,'* Identical-input control, conditional on the recorded packet-equivalence audit; no additional model calls.',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1));save(fig,a.output,'controls')
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.2),sharey=True)
    for ax,provider in zip(axs,MODELS):
        for i,arm in enumerate(['company','gtm','full']):
            r=idx[(provider,arm)];value=r['mean_normalized_value']*100;available=r['context_value']*100
            if value>available+1e-7:raise ValueError('reader exceeded grounded context ceiling')
            ax.bar(i,value,color='#397F68',label='Returned grounded value' if i==0 else None)
            ax.bar(i,available-value,bottom=value,color='#E5BA72',label='Available but not returned' if i==0 else None)
            ax.bar(i,100-available,bottom=available,color='#D8DDE4',label='Not supported by context' if i==0 else None)
        ax.set_xticks(range(3),['Company','GTM','Full']);ax.set_title(MODELS[provider]);grid(ax)
    axs[0].set_ylabel('Share of full-information optimum (%)');handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,ncol=3,loc='lower center',fontsize=8)
    fig.tight_layout(rect=(0,.08,1,1));save(fig,a.output,'decomposition')
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.2),sharey=True)
    for ax,provider in zip(axs,MODELS):
        for arm in ARMS:
            r=idx[(provider,arm)];x=r['estimated_usd']/r['cases']*1000;y=r['mean_normalized_value']*100
            ax.scatter(x,y,c=COLORS[arm],s=55);ax.annotate({'none':'No context','company':'Company','gtm':'GTM','markdown':'Markdown','gbrain':'GBrain','full':'Full'}[arm],(x,y),xytext=(5,18 if arm=='none' else 5 if arm!='markdown' else -13),textcoords='offset points',fontsize=8)
        ax.set_title(MODELS[provider]);ax.set_xlabel('Reader API USD per 1,000 queries');grid(ax);ax.set_ylim(-4,108);ax.margins(x=.25)
    axs[0].set_ylabel('Grounded policy value (%)');fig.tight_layout();save(fig,a.output,'cost')
    fig,ax=plt.subplots(figsize=(7.2,2.4));ax.set_xlim(0,12);ax.set_ylim(0,4.7);ax.axis('off')
    def box(x,y,w,h,text,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08',facecolor=color,edgecolor='#526071',lw=.8));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=8)
    box(.15,1.4,2.4,1.35,'Same records\nApproved policy\nCurrent + permitted','#E9EEF4')
    for y,arm in [(3.15,'none'),(1.65,'company'),(.15,'gtm')]:
        box(3.3,y,2.4,.9,{'none':'No company\ncontext','company':'Company\ncontext','gtm':'GTM context'}[arm],COLORS[arm]);ax.annotate('',xy=(3.18,y+.45),xytext=(2.68,2.075),arrowprops={'arrowstyle':'->','color':'#526071'})
        ax.annotate('',xy=(6.4,2.075),xytext=(5.83,y+.45),arrowprops={'arrowstyle':'->','color':'#526071'})
    box(6.55,1.4,2.4,1.35,'Fixed reader\nGPT or Opus\nShared task/catalog','#E9EEF4')
    box(9.55,1.4,2.25,1.35,'Grounded plan\nDistinct accounts\nShared allowance','#E9EEF4')
    ax.annotate('',xy=(9.43,2.075),xytext=(9.08,2.075),arrowprops={'arrowstyle':'->','color':'#526071'})
    ax.text(6,4.5,'Measure evidence availability, then reader decisions',ha='center',fontsize=9,fontweight='bold')
    save(fig,a.output,'design')
    if a.budget:
        b=json.loads(a.budget.read_text());fig,ax=plt.subplots(figsize=(7.2,3.2))
        for arm in ['company','gtm','markdown','gbrain']:
            rows=sorted([x for x in b['summary'] if x['arm']==arm],key=lambda x:x['budget_bytes'])
            ax.plot([x['budget_bytes']/1024 for x in rows],[x['mean_normalized_recoverable_value']*100 for x in rows],marker='o',color=COLORS[arm],label=LABELS[arm],lw=2)
        ax.set_xscale('log',base=2);ax.set_xticks([4,8,16,32,64,128],[4,8,16,32,64,128]);ax.set_xlabel('Evidence allowance (KiB; shared cases and facts)')
        ax.set_ylabel('Recoverable policy value (%)');grid(ax);ax.legend(fontsize=9,loc='lower right')
        ax.set_title('Retrieval-only sensitivity — no extra reader calls');fig.tight_layout();save(fig,a.output,'budget')
    lines=['\\begin{tabular}{llrrrr}','\\toprule','Reader & Context & Value (\\%) & Exact / positive & Unsupported / all & API USD \\\\', '\\midrule']
    for provider in MODELS:
        for arm in ARMS:
            r=idx[(provider,arm)];label={'none':'None','company':'Company','gtm':'GTM','markdown':'Markdown','gbrain':'GBrain search','full':'Full context'}[arm]
            lines.append(f"{MODELS[provider]} & {label} & {r['mean_normalized_value']*100:.1f} & {r['exact_positive']}/{r['positive_cases']} & {r['unsafe_all']}/{r['cases']} & {r['estimated_usd']:.2f} \\\\")
        lines.append('\\midrule')
    lines[-1]='\\bottomrule';lines.append('\\end{tabular}')
    (a.output/'results-table.tex').write_text('\n'.join(lines)+'\n')
    resource=['\\begin{tabular}{llrrrr}', '\\toprule', 'Reader & Context & Input/query & Output/query & Seconds/query & USD/1,000 \\\\', '\\midrule']
    for provider in MODELS:
        for arm in ['none','company','gtm','full']:
            r=idx[(provider,arm)];n=r['cases']
            resource.append(f"{MODELS[provider]} & {('GTM' if arm=='gtm' else arm.title())} & {r['input_tokens']/n:,.0f} & {r['output_tokens']/n:,.0f} & {r['mean_seconds']:.1f} & {1000*r['estimated_usd']/n:.2f} \\\\")
        resource.append('\\midrule')
    resource[-1]='\\bottomrule';resource.append('\\end{tabular}')
    (a.output/'resource-table.tex').write_text('\n'.join(resource)+'\n')
    if a.external:
        external=json.loads(a.external.read_text());order=['none','raw_bm25','raw_chunks','raw_full','wiki_generic','wiki_specialized']
        names=['No context','Whole-doc BM25','Chunked BM25','Full raw documents','General wiki','Marketing wiki']
        colors=[COLORS['none'],COLORS['company'],COLORS['company'],COLORS['full'],COLORS['company'],COLORS['gtm']]
        fig,ax=plt.subplots(figsize=(7.2,3.3));values=[external['groups'][arm]['correct'] for arm in order]
        ax.barh(range(len(order)),values,color=colors,height=.65);ax.set_yticks(range(len(order)),names);ax.invert_yaxis();ax.set_xlim(0,24)
        for i,value in enumerate(values):ax.text(value+.25,i,f'{value}/22',va='center',fontweight='bold')
        ax.set_xlabel('Correct development answers (one company; Claude Opus 5.5)');ax.set_xticks([0,5,10,15,20,22]);ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
        fig.tight_layout();save(fig,a.output,'external')
        lines=['\\begin{tabular}{lrrr}', '\\toprule', 'Context & Correct / 22 & Excluding ambiguous item / 21 & Reader USD \\\\', '\\midrule']
        for arm,name in zip(order,names):
            r=external['groups'][arm];lines.append(f"{name} & {r['correct']} & {r['excluding_ambiguous_label_correct']} & {float(r['estimated_usd']):.2f} \\\\")
        lines+=['\\bottomrule','\\end{tabular}'];(a.output/'external-table.tex').write_text('\n'.join(lines)+'\n')
    metrics={'worlds':s['worlds'],'cases':s['cases'],'attempts':s['attempts'],'completed':s['completed'],'failed':s['failed'],'main_estimated_usd':float(s['estimated_usage_usd']),
             'summary':s['summary'],'contrasts':s['contrasts'],'full_to_gtm_reader_cost_ratio':{provider:idx[(provider,'full')]['estimated_usd']/idx[(provider,'gtm')]['estimated_usd'] for provider in MODELS},'source_sha256':sha(a.summary.read_bytes())}
    dump(a.output/'metrics.json',metrics)
    macros={'ChallengeWorlds':str(s['worlds']),'ChallengeCases':str(s['cases']),'ChallengeCalls':format(s['attempts'],','),'ChallengeCompleted':format(s['completed'],','),'ChallengeFailures':str(s['failed']),
            'ChallengePositives':str(idx[('openai','gtm')]['positive_cases']),'ChallengeNegatives':str(idx[('openai','gtm')]['negative_cases']),'ChallengeCost':f"{float(s['estimated_usage_usd']):.2f}"}
    for provider,tag in [('openai','GPT'),('anthropic','Opus')]:
        for arm,name in [('none','None'),('company','Company'),('gtm','GTM'),('full','Full')]:macros[tag+name]=f"{idx[(provider,arm)]['mean_normalized_value']*100:.1f}"
        c=next(c for c in s['contrasts'] if c['provider']==provider and c['control']=='company')
        macros[tag+'Gain']=f"{c['difference']*100:.1f}";macros[tag+'Lower']=f"{c['ci95'][0]*100:.1f}";macros[tag+'Upper']=f"{c['ci95'][1]*100:.1f}"
    (a.output/'numbers.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items())+'\n')
    print(json.dumps({'figures':6+bool(a.budget)+bool(a.external),'output':str(a.output),'source_sha256':metrics['source_sha256']}))

if __name__=='__main__':main()
