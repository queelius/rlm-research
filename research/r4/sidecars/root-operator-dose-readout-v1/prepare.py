"""Copy immutable planned inputs; qualify authored native boundaries; no science sampling."""
import asyncio
import json
from pathlib import Path
import dr_study as s

def main():
    s.dose.verify();files=[]
    for path in sorted((s.TRAINING/'inputs').glob('*.json')):
        if path.name=='PARAMETER_MAP.json':continue
        destination=s.ROOT/'inputs'/path.name;destination.parent.mkdir(parents=True,exist_ok=True)
        # Preserve literal source bytes: integer-key histogram JSON reserialization can reorder keys.
        with destination.open('xb') as stream:stream.write(path.read_bytes())
        if s.sha(destination)!=s.sha(path):raise ValueError('frozen input bytes changed')
        files.append(dict(source=str(path),target=str(destination),sha256=s.sha(path)))
    template=s.OLD/'inputs/NATIVE_TEMPLATE.json';s.write(s.ROOT/'inputs/NATIVE_TEMPLATE.json',s.read(template))
    s.write(s.ROOT/'INPUT_RECEIPT.json',dict(frozen_training_ready_sha256=s.TRAIN_READY_SHA,files=files,native_template_source=str(template),native_template_sha256=s.sha(template),planned_full=96,planned_first_action=24,policy_selection='fixed6/fixed24 only',training_source_modified=False))
    contexts={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};prompts=s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json');rows=s.read(s.ROOT/'inputs/FREE_PLAN.json');audits=[]
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,value):self.files[name]=value
    async def setup(task):
        memory=Memory();await task.setup(None,memory);return memory.files
    for row in rows:
        ctx=contexts[row['context_id']];task=s.stack().native.task(ctx,prompts[row['id']]['prompt'],0,row['id']);changed=s.stack().native.task(ctx,prompts[row['id']]['prompt'],999999,row['id'])
        a=asyncio.run(setup(task));b=asyncio.run(setup(changed))
        if a!=b or s.o.qnative().first_prefix(task)!=prompts[row['id']]['token_ids']:raise ValueError('gold leak or native prefix drift')
        if json.loads(a['records.json'])!=ctx['records'] or a['query.txt']!=row['question'].encode():raise ValueError('actual native files differ')
        audits.append(dict(id=row['id'],prefix_tokens=len(prompts[row['id']]['token_ids']),files_sha256={n:__import__('hashlib').sha256(v).hexdigest() for n,v in a.items()},source_split=task.data.source_split,gold_independent=True,policy_independent=True))
    s.write(s.ROOT/'CPU_INPUT_NATIVE.json',dict(rows=audits,full=48,policies=2,max_prefix=max(x['prefix_tokens'] for x in audits),all_native_prefixes_equal=True,all_files_policy_independent=True,metadata_caveat='root-new is previously prepared and child-training-exposed; only metadata corrected; frozen prompt/file bytes unchanged'))
    print(dict(prepared=True,full=96,first_action=24,max_prefix=max(x['prefix_tokens'] for x in audits)))

if __name__=='__main__':main()
