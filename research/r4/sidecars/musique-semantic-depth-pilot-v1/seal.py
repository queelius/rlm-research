"""One CPU qualification and immutable transitive input/source closure."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import musique_study as s


def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
    if (s.ROOT/'READY.json').exists() or s.ATTEMPT.exists():raise FileExistsError('fresh seal required')
    condition=s.runtime_condition()
    if not condition['qualified']:raise ValueError('accepted native runtime unavailable')
    argv=[str(s.NATIVE),'-m','pytest','-q','test_pilot.py','--basetemp',str(s.ROOT/'cpu-fixture-v2')]
    if (s.ROOT/'cpu-fixture-v2').exists():raise FileExistsError('do not overwrite a prior fixture')
    started=time.time()
    result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},
                          capture_output=True,text=True,timeout=180)
    s.write_x(s.ROOT/'CPU_TESTS_V2.json',{'argv':argv,'returncode':result.returncode,'stdout':result.stdout,
        'stderr':result.stderr,'elapsed_seconds':time.time()-started,'model_weight_loads':0,'GPU_calls':0,
        'scope':'two focused fixtures, actual cached CPU nano container and native fake provider, not scientific inference'})
    if result.returncode:raise ValueError(result.stdout+result.stderr)
    # Resolve service functions now, not a constructor-only promise.
    suite=s.dependencies();binding=s.binding();recorder=s.recorder()
    for name in ('start_service','release_service','command'):
        if not callable(getattr(suite,name,None)):raise ValueError('service interface missing: '+name)
    closure={};pending=[s.SHORT/'READY_V2.json',s.FEASIBILITY/'FEASIBILITY_READY.json']
    traversed=set()
    while pending:
        path=Path(pending.pop()).resolve()
        if path in traversed:continue
        traversed.add(path);closure[str(path)]=s.sha(path)
        if path.suffix!='.json':continue
        value=s.read(path)
        if not isinstance(value,dict):continue
        for key in ('closure_sha256','files_sha256','source_sha256','source_hashes'):
            mapping=value.get(key,{})
            if not isinstance(mapping,dict):continue
            for name,expected in mapping.items():
                target=Path(name)
                if not target.is_absolute() or not target.is_file() or not isinstance(expected,str) or len(expected)!=64:continue
                actual=s.sha(target)
                if actual!=expected:raise ValueError('inherited closure changed: '+name)
                closure[str(target.resolve())]=actual
                if target.suffix=='.json' and ('READY' in target.name or 'MANIFEST' in target.name):pending.append(target)
    files=[p for p in s.ROOT.glob('*') if p.is_file() and p.name!='READY.json']
    files+=list(s.INPUTS.rglob('*'))+list((s.ROOT/'cpu-fixture').rglob('*'))+list((s.ROOT/'cpu-fixture-v2').rglob('*'))
    files+=[Path(suite.__file__),Path(recorder.__file__),s.NATIVE.resolve()]
    # Pin the actual imported local framework/renderer sources, avoiding unresolved
    # dependency pointers or indiscriminate unrelated environment inventories.
    for module in list(sys.modules.values()):
        raw=getattr(module,'__file__',None)
        if raw and raw.endswith('.py') and ('/verifiers/' in raw or '/renderers/' in raw):files.append(Path(raw))
    for path in files:
        if path.is_file():closure[str(path.resolve())]=s.sha(path)
    packages={}
    for name in ('verifiers','renderers','transformers','tokenizers','torch','vllm','openai','httpx','aiohttp','pydantic'):
        try:packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:packages[name]=None
    value={'schema':'musique-semantic-depth-pilot-ready-v1','status':'READY_FOR_MAIN_REVIEW',
        'created_epoch':time.time(),'runtime_condition':condition,'binding':binding,
        'root_and_child_policy':s.MODEL_ALIAS,'adapter':None,'examples':12,'planned_episodes':48,
        'max_physical_calls':228,'depths':[0,1,2],'question_only_calls_per_question':1,
        'native_output_tokens_per_call':1024,'actual_prompt_plus_output_cap':8192,'temperature':.5,
        'seed_base':202609132000,'call_reservation_before_await':True,'optimizer_steps':0,
        'caps':{'science':s.SCIENCE_SECONDS,'owner':s.OWNER_SECONDS,'external':s.EXTERNAL_SECONDS},
        'fixed_argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT),'--outer-seconds','1700'],
        'GPU_launch_authority':'MAIN only after independent review/shared flock',
        'python':sys.version,'packages':packages,'cpu_receipt_sha256':s.sha(s.ROOT/'CPU_TESTS_V2.json'),
        'data_manifest_sha256':s.sha(s.INPUTS/'MANIFEST.json'),'closure_sha256':dict(sorted(closure.items()))}
    value['identity']=s.digest(value);s.write_x(s.ROOT/'READY.json',value)
    print(json.dumps({'ready_sha256':s.sha(s.ROOT/'READY.json'),'identity':value['identity'],
        'pins':len(closure),'tests':result.stdout.strip()}))


if __name__=='__main__':main()
