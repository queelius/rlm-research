"""CPU-only fresh input selection; no service or model calls."""
import importlib.util,time
from pathlib import Path
import protocol as p,study as s

PARQUET=Path('/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2/validation_matched.parquet')
CHECK=s.SIDE.parent/'analyses/mnli-new-context-feasibility-2026-09-10/check_v2.py'
CHECK_PIN='a2760181e19ebed8e943358ac709585ef444d4df11783fdb96a161e4bd77f937'
def selection_module():
    if s.sha(CHECK)!=CHECK_PIN:raise ValueError('selection source changed')
    spec=importlib.util.spec_from_file_location('visible_reference_selection',CHECK);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.MASTER=p.MASTER;return m
def inputs():
    import pyarrow.parquet as pq
    scan_start=time.time();f=selection_module();excluded=set(s.read(f.BASE/'EXPOSURE.json')['exact_text_hits']);named=[];visible=set();prior_groups=set()
    for directory in sorted(s.SIDE.glob('*mnli*')):
        if directory==s.ROOT:continue
        for name in ('DATA.json','PUBLIC.json','PLAN.json','REQUESTS.json','READY.json','READY_v2.json'):
            path=directory/name
            if not path.exists():continue
            named.append(path)
            if name not in ('DATA.json','PUBLIC.json'):continue
            value=s.read(path);contexts=value.get('contexts',value) if isinstance(value,dict) else value
            for context in contexts:
                prior_groups.update(context.get('premise_groups',[]))
                for row in context['records']:
                    for field in ('premise','hypothesis'):excluded.add(f.group(row[field]))
                    visible.add(row['id'])
    if s.sha(PARQUET)!='350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186':raise ValueError('source parquet changed')
    source_rows=pq.read_table(PARQUET).to_pylist();all_contexts,eligible,conflicts=f.select(source_rows,excluded)
    contexts=[]
    for genre in f.GENRES:
        candidates=[c for c in all_contexts if c['genre']==genre][:2]
        if len(candidates)!=2:raise ValueError('insufficient selected contexts '+genre)
        contexts.extend(candidates)
    for index,context in enumerate(contexts):context['index']=index
    mutated=[{**row,'label':int(f.digest([p.MASTER,'label-mutation',i]),16)%3} for i,row in enumerate(source_rows)];changed_all,_,_=f.select(mutated,excluded);changed=[]
    for genre in f.GENRES:changed.extend([c for c in changed_all if c['genre']==genre][:2])
    overlap=sorted(prior_groups&{group for context in contexts for group in context['premise_groups']})
    if f.public(changed)!=f.public(contexts) or overlap or conflicts:raise ValueError('selection invariant')
    s.write(s.ROOT/'DATA.json',{'contexts':contexts});s.write(s.ROOT/'PUBLIC.json',[{'index':c['index'],'genre':c['genre'],'premise_groups':c['premise_groups'],'records':[{k:r[k] for k in ('id','premise','hypothesis')} for r in c['records']]} for c in contexts])
    s.write(s.ROOT/'SELECTION_AUDIT.json',{'scan_started_epoch':scan_start,'scan_ended_epoch':time.time(),'master':p.MASTER,'named_paths':[str(x) for x in named],'named_sha256':{str(x):s.sha(x) for x in named},'excluded_normalized_text_hashes':len(excluded),'eligible_premise_groups':eligible,'source_rows':len(source_rows),'selected_contexts':8,'selected_premise_groups':128,'prior_selected_overlap':overlap,'label_mutation_invariant':True,'source_parquet_sha256':s.sha(PARQUET),'scope':'named inventories; not globally or pretraining unseen'})

if __name__=='__main__':inputs()
