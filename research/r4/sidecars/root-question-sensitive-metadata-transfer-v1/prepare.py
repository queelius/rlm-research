"""Freeze all public metadata counterfactuals and gold-independent native files."""
import asyncio
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
import study as s

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('immutable selection, no reroll')
    started=time.time();contexts,plan=s.transfer_inputs();public={c['id']:c for c in contexts}
    old_gold=s.read(s.ORIGINAL/'inputs/HOST_GOLD.json');gold={cid:dict(labels=old_gold[cid]['labels'],answers={}) for cid in public}
    prompts={};checks=[]
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        mem=Memory();await task.setup(None,mem);return mem.files
    for row in plan:
        context=public[row['context_id']];labels=gold[context['id']]['labels']
        answer=s.base.problem.answer(context['records'],labels,row)
        if answer!=s.base.problem.enumerated_answer(context['records'],labels,row):raise ValueError('independent oracle mismatch')
        gold[context['id']]['answers'][row['family']]=answer
        task=s.base.make_task(context,row,0);other=s.base.make_task(context,row,999999)
        prefix=s.base.qnative().first_prefix(task);a=asyncio.run(files(task));b=asyncio.run(files(other))
        if a!=b or prefix!=s.base.qnative().first_prefix(other) or len(prefix)+2048>8192:raise ValueError('gold or budget violation')
        if set(a)!={'records.json','context.txt','query.txt','batch_contract.py'} or json.loads(a['records.json'])!=context['records'] or a['query.txt']!=row['question'].encode():raise ValueError('actual public files differ')
        prompts[row['id']]=dict(prompt=task.data.prompt,plain_query=row['question'],token_ids=prefix)
        checks.append(dict(id=row['id'],prefix_tokens=len(prefix),gold_independent=True,exact_four_files=True,files_sha256={k:hashlib.sha256(v).hexdigest() for k,v in a.items()}))
    histogram=Counter(gold[r['context_id']]['answers'][r['family']] for r in plan)
    values={'FREE_PLAN.json':plan,'PUBLIC.json':contexts,'HOST_GOLD.json':gold,'PROMPTS_ACCURATE.json':prompts,
        'NATIVE_TEMPLATE.json':s.read(s.ORIGINAL/'inputs/NATIVE_TEMPLATE.json'),
        'PROVENANCE.json':dict(original_groups_path=str(s.ORIGINAL/'inputs/GROUPS.json'),original_groups_sha256=s.sha(s.ORIGINAL/'inputs/GROUPS.json'),all_original72_protected_questions=True,source_text_and_labels_unchanged=True,child_training_exposed=True,metadata_shift=True,no_selection_by_gold=True,gold_histogram=dict(histogram),zero=histogram[0],new_groups=False)}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_NATIVE.json',dict(checks=checks,scientific_calls=0,elapsed_seconds=time.time()-started))
    sources={str(p):s.sha(p) for p in s.ROOT.glob('*.py')}
    sources.update(s.read(s.ORIGINAL/'READY.json')['source_sha256'])
    for p in (s.ROOT/'DESIGN.md',s.ORIGINAL/'READY.json',s.RECOVERY/'POSTCAPTURE_GPU_READY.json'):sources[str(p)]=s.sha(p)
    for arm in ('unchanged','sft6'):
        for model in s.binding(arm)['models'].values():
            path=Path(model['path'])
            for name in ('adapter_model.safetensors','adapter_config.json'):
                if (path/name).exists():sources[str(path/name)]=s.sha(path/name)
    for name in ('postcapture_binding.py','recovery_binding_v3.py','recovery_study_v3.py'):
        p=s.RECOVERY/name;sources[str(p)]=s.sha(p)
    ready=dict(source_sha256=sources,input_sha256={str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')},planned=144,policy_order=['sft6','unchanged'],seed_range=[988621001,988621072],new_training=False,changed_metadata=['user_names','weights','thresholds'])
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    print(dict(identity=ready['identity'],prepared=72,elapsed_seconds=time.time()-started,zeros=histogram[0]))
if __name__=='__main__':main()
