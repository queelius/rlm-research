"""CPU immutable source selection/rendering, focused tests and readiness closure."""
import argparse
import ast
import os
import subprocess
import time
from pathlib import Path
import transfer_study as s
import transfer_data as d

def inputs():
    values=d.build();template=s.read(s.OLD/'inputs/NATIVE_TEMPLATE.json');values['NATIVE_TEMPLATE.json']=template
    renderer=s.stack().native.renderer();public={c['id']:c for c in values['PUBLIC.json']};prompts={}
    import json
    for row in values['FREE_PLAN.json']:
        prompt=d.prompt(public[row['context_id']],row);ids=renderer.render([template['system'],dict(role='user',content=prompt)],tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
        if len(ids)+2048>8192:raise ValueError('native first prefix budget; no truncation')
        prompts[row['id']]=dict(prompt=prompt,token_ids=ids)
    values['PROMPTS_ACCURATE.json']=prompts
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    print(dict(contexts=4,groups=64,free_per_policy=16,planned=48))

def qualify():
    argv=[str(s.NATIVE),'-m','unittest','-v','test_data','test_entry','test_native','test_lifecycle','test_collect']
    started=time.time();result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    for path in s.ROOT.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    value=dict(passed=result.returncode==0,argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started,source_sha256={str(p):s.sha(p) for p in s.ROOT.glob('*.py')},gpu_calls=0,model_service_calls=0)
    s.write(s.ROOT/'CPU_TESTS.json',value)
    if not value['passed']:raise ValueError('focused CPU tests failed; retained evidence')
    print(dict(passed=True,sha256=s.sha(s.ROOT/'CPU_TESTS.json')))

def seal():
    tests=s.read(s.ROOT/'CPU_TESTS.json')
    if not tests['passed']:raise ValueError('CPU tests required')
    for path,pin in tests['source_sha256'].items():s.check(path,pin)
    prior=s.source.verify();sources=dict(prior['source_sha256']);inputs=dict(prior['input_sha256'])
    for p in [*s.ROOT.glob('*.py'),*s.ROOT.glob('*.md'),s.ROOT/'CPU_TESTS.json',s.OLD/'READY.json']:sources[str(p)]=s.sha(p)
    for p in (s.ROOT/'inputs').glob('*.json'):inputs[str(p)]=s.sha(p)
    proof=s.read(s.ROOT/'inputs/PROVENANCE.json');sources.update(proof['source_sha256'])
    receipt=s.read(s.QSR/'inputs/PROVENANCE.json')['receipt_path']
    for item in s.read(receipt)['files']:sources[item['path']]=item['sha256']
    import transfer_binding as b
    selections={arm:b.selected(arm) for arm in s.ARMS}
    for arm,chosen in selections.items():
        directory=Path(chosen['checkpoint']);state=s.read(directory/'state.json');sources[str(directory/'state.json')]=s.sha(directory/'state.json')
        for name,pin in state['files_sha256'].items():sources[str(directory/name)]=pin
        if arm!='unchanged':
            for p in [directory.parent/'SELECTION.json',directory.parent/'RESULT.json']:sources[str(p)]=s.sha(p)
    for path,pin in {**sources,**inputs}.items():s.check(path,pin)
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=sources,input_sha256=inputs,selections=selections,planned=48,contexts=4,groups=64,free_per_policy=16,phase_order=s.phases(),work_seconds=2100,owned_seconds=2280,outer_seconds=2400,phase_cap_seconds=480,per_episode_seconds=180,workers=4,no_training=True,no_rerolls=True,child_sha256=s.CHILD_SHA,master_seed=s.MASTER,argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],gpu_calls=0,prepared_epoch=time.time())
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value);s.verify();print(dict(sha256=s.sha(s.ROOT/'READY.json'),identity=value['identity']))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal','verify'));args=ap.parse_args()
    if args.command=='inputs':inputs()
    elif args.command=='qualify':qualify()
    elif args.command=='seal':seal()
    else:print(s.verify()['identity'])
