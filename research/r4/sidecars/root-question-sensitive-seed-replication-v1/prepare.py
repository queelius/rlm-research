"""Freeze fresh seeds/IDs with identical public question and native prefix."""
import asyncio
import time
import study as s

def main():
    if (s.ROOT/'inputs').exists():raise FileExistsError('no reroll')
    started=time.time();old=s.read(s.ORIGINAL/'inputs/FREE_PLAN.json');plan=s.build_plan(old)
    contexts=[c for c in s.read(s.ORIGINAL/'inputs/PUBLIC.json') if c['split']=='protected']
    for c in contexts:c['native_context_id']+=2000000
    public={c['id']:c for c in contexts};prompts={};checks=[]
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        mem=Memory();await task.setup(None,mem);return mem.files
    old_prompts=s.read(s.ORIGINAL/'inputs/PROMPTS_ACCURATE.json')
    for before,row in zip(old,plan):
        task=s.base.make_task(public[row['context_id']],row,0)
        other=s.base.make_task(public[row['context_id']],row,999999)
        prefix=s.base.qnative().first_prefix(task)
        if prefix!=old_prompts[before['id']]['token_ids']:raise ValueError('question or prefix changed')
        if asyncio.run(files(task))!=asyncio.run(files(other)):raise ValueError('private gold leakage')
        prompts[row['id']]={**old_prompts[before['id']]}
        checks.append(dict(id=row['id'],prior_id=before['id'],same_prefix=True,prefix_tokens=len(prefix),gold_independent=True))
    for name,value in {'FREE_PLAN.json':plan,'PUBLIC.json':contexts,
        'HOST_GOLD.json':{k:v for k,v in s.read(s.ORIGINAL/'inputs/HOST_GOLD.json').items() if k in public},
        'PROMPTS_ACCURATE.json':prompts,'NATIVE_TEMPLATE.json':s.read(s.ORIGINAL/'inputs/NATIVE_TEMPLATE.json')}.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'CPU_NATIVE.json',dict(checks=checks,scientific_calls=0,elapsed_seconds=time.time()-started))
    sources={str(p):s.sha(p) for p in s.ROOT.glob('*.py')}
    for p in (s.ROOT/'DESIGN.md',s.ORIGINAL/'READY.json',s.RECOVERY/'POSTCAPTURE_GPU_READY.json'):sources[str(p)]=s.sha(p)
    sources.update(s.read(s.ORIGINAL/'READY.json')['source_sha256'])
    for arm in ('unchanged','sft6'):
        binding=s.binding(arm)
        for model in binding['models'].values():
            path=s.ROOT.__class__(model['path'])
            for name in ('adapter_model.safetensors','adapter_config.json'):
                if (path/name).exists():sources[str(path/name)]=s.sha(path/name)
    for name in ('postcapture_binding.py','recovery_binding_v3.py','recovery_study_v3.py'):
        p=s.RECOVERY/name;sources[str(p)]=s.sha(p)
    ready=dict(source_sha256=sources,input_sha256={str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')},
        planned=144,policy_order=['sft6','unchanged'],seed_range=[987621001,987621072],new_training=False)
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    print(dict(identity=ready['identity'],prepared=72,elapsed_seconds=time.time()-started))
if __name__=='__main__':main()
