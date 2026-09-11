"""Freeze all12 historical inputs without new acquisition or outcome selection."""
import argparse
import ast
import os
from pathlib import Path
import subprocess
import time
import study as s
import protocol as p

def inputs():
    audit=s.read(s.AUDIT/'FINAL_MANIFEST.json')
    for path,pin in audit['source_sha256'].items():
        if s.sha(path)!=pin:raise ValueError('sealed audit changed')
    directory=s.PILOT/'outputs/attempt-001';tokenizer=s.tokenizer();sources=[];pins={}
    def pinned(path):pins[str(path)]=s.sha(path);return s.read(path)
    all_direct=[(path,pinned(path)) for path in sorted((directory/'calls').glob('*-direct_expanded.json'))]
    direct={}
    for path,call in all_direct:
        world=call['id'].split('-')[1];key='world-'+world
        if key in direct:
            other=direct[key][1]
            if call['prompt_token_ids']!=other['prompt_token_ids'] or call['request']['messages']!=other['request']['messages']:raise ValueError('direct worlds not genuinely duplicated')
        else:direct[key]=(path,call)
    chosen=[(path,pinned(path),'full') for path in sorted((directory/'calls').glob('*-parent-full.json'))]
    chosen.extend((path,call,'direct') for path,call in direct.values())
    gold={w['id']:w['gold'] for w in pinned(s.PILOT/'WORLDS.json')}
    for index,(path,call,kind) in enumerate(chosen):
        world='world-'+call['id'].split('-')[1];coordinate=call['id'].removesuffix('-parent-full');acquisitions=[]
        if kind=='full':
            reports=pinned(directory/'reports'/f'{coordinate}.json')['full']
            if s.serialize(reports['reports']) not in call['request']['messages'][1]['content']:raise ValueError('actual report serialization not present unchanged')
            for identifier in reports['acquisition_call_ids']:
                childpath=directory/'calls'/f'{identifier}.json';child=pinned(childpath)
                acquisitions.append(dict(path=str(childpath),sha256=s.sha(childpath),prompt_tokens=child['prompt_tokens'],output_tokens=child['output_tokens'],seconds=child['seconds']))
        messages=call['request']['messages'];native=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=False)
        if native!=call['prompt_token_ids'] or len(native)+2560>8192:raise ValueError('native/historical exact prompt or context mismatch')
        source=dict(id=f'input-{index:02}',world_id=world,kind=kind,partition=call['id'].split('-')[2] if kind=='full' else None,
            messages=messages,historical_prompt_token_ids=call['prompt_token_ids'],actual_native_prompt_token_ids=native,
            historical_call_path=str(path),historical_call_sha256=s.sha(path),acquisitions=acquisitions,acquisition_cost=p.acquisition_cost(acquisitions),seed=981360001+index)
        sources.append(source)
    if len(sources)!=12 or len(direct)!=4 or len({s.digest(x['actual_native_prompt_token_ids']) for x in sources})!=12:raise ValueError('all12 unique inputs required')
    plan=[];requests={}
    for index,source in enumerate(sources):
        for decoder in (('free','exact') if index%2==0 else ('exact','free')):
            row=dict(source_id=source['id'],world_id=source['world_id'],kind=source['kind'],partition=source['partition'],decoder=decoder,seed=source['seed'],dispatch_order=len(plan))
            row['id']=s.digest([s.ROOT.name,row]);plan.append(row);requests[row['id']]=p.request(source,row['seed'],decoder,s.MODEL['alias'])
    for name,value in [('INPUTS.json',sources),('HOST_GOLD.json',gold),('PLAN.json',plan),('REQUESTS.json',requests),('SOURCE_PINS.json',pins)]:s.write(s.ROOT/name,value)
    s.write(s.ROOT/'PROVENANCE.json',dict(audit_manifest_sha256=s.sha(s.AUDIT/'FINAL_MANIFEST.json'),unique_full_states=8,unique_direct_worlds=4,
        historical_unique_extraction_calls=24,new_extraction_calls=0,new_final_calls=24,hypothetical_acquisition_calls_across_full_endpoints=48,
        fresh_seed_range=[981360001,981360012],seed_audit='before source creation rg of existing PLAN/SPEC/SEED/READY files found zero matches for9813600xx',
        exposure='All4 engineered worlds/outcomes already research-exposed; no selected successful subset; source ordering fixed before new sampling',
        causal_scope='within-pair final decoder difference only; historical HF/backend/cap comparison descriptive',native_prompt_identity='historical HF IDs equal prospective common vLLM native tokenizer IDs; actual service IDs checked on every return'))
    print(dict(inputs=12,requests=24,acquisitions_new=0))

def qualify():
    argv=[str(s.NATIVE),'-m','unittest','-v','test_contracts','test_native_cpu']
    result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    for path in s.ROOT.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    value=dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,passed=result.returncode==0,gpu_calls=0,service_calls=0,
        source_sha256={str(path):s.sha(path) for path in s.ROOT.glob('*.py')})
    s.write(s.ROOT/'CPU_TESTS.json',value)
    if result.returncode:raise ValueError('focused tests failed; artifact retained')
    print(dict(passed=True,cpu_tests_sha256=s.sha(s.ROOT/'CPU_TESTS.json')))

def seal():
    tests=s.read(s.ROOT/'CPU_TESTS.json')
    if not tests['passed'] or any(s.sha(path)!=pin for path,pin in tests['source_sha256'].items()):raise ValueError('fresh matching CPU qualification required')
    source=dict(s.read(s.FREE/'READY_RECOVERY3.json')['source_sha256'])
    source.update(s.read(s.RUNTIME/'LIFECYCLE_READY_V2.json')['source_sha256'])
    source.update(s.read(s.ROOT/'SOURCE_PINS.json'))
    for path in [*s.ROOT.glob('*.py'),*s.ROOT.glob('*.json'),*s.ROOT.glob('*.md'),s.AUDIT/'FINAL_MANIFEST.json',s.AUDIT/'REPORT.md',s.FREE/'READY_RECOVERY3.json']:
        source[str(path)]=s.sha(path)
    for path,pin in source.items():
        if s.sha(path)!=pin:raise ValueError('immutable closure mismatch: '+path)
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,planned_calls=24,unique_inputs=12,world_clusters=4,
        outer_seconds=900,work_seconds=780,cleanup_seconds=90,parent_margin_seconds=30,collection_seconds=600,readiness_seconds=180,
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],model=s.MODEL,adapter=None,
        service_wrapper=str(s.FREE/'service_wrapper_v3.py'),credentials='MAIN privately binds STRICT_RLM_CALIBRATION_API_KEY; never argv/logs',
        gpu_calls=0,service_calls=0,actual_calls_still_pending=True,prepared_epoch=time.time())
    value['identity']=s.digest(value);s.write(s.ROOT/'READY.json',value);print(s.sha(s.ROOT/'READY.json'))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));args=ap.parse_args();globals()[args.command]()
