"""New state-content factorial over pinned native low66c/c32 and proven restart runtime."""
import functools
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'root-corrective-reduction-sft-v1'
RUNTIME=ROOT.parent/'runtime-an27-5780-v1'
ATTEMPT=ROOT/'outputs/attempt-001'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def load(name,path,pin):
    if sha(path)!=pin:raise ValueError('source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

@functools.lru_cache(maxsize=1)
def source():return load('restart_corrective_source',SOURCE/'study.py','5e509fcc7285acb443b43f81491377eb76dbfd58e5d194e9c676a641a16246de')

@functools.lru_cache(maxsize=1)
def stack():
    st=source().stack();st.prior.ROOT=ROOT
    st.prior.context_window_id=lambda c:c['native_context_id']
    sys.path.insert(0,str(ROOT));return st

def runtime():
    result=source().runtime();sys.path.insert(0,str(ROOT));return result

def interface(output):
    wrapper,_=runtime();st=wrapper.adapt_stack(stack())
    with source().aliases({'interface':st.interface}):value=st.local.configure_interface(output)
    sys.path.insert(0,str(ROOT));return value

def task(context,prompt,goal,row,files,setup_output=None):
    original=stack().native.task(context,prompt,0,row['id'])
    class RestartTask(type(original)):
        async def setup(self,trace,runtime):
            started=time.time();await super().setup(trace,runtime)
            result=await runtime.run(['mkdir','-p','state'],{})
            if result.exit_code:raise ValueError('artifact directory setup failed')
            for name,text in files.items():await runtime.write(name,text.encode())
            expected={**files,'query.txt':goal,'records.json':json.dumps(context['records'],ensure_ascii=False),'context.txt':context['text'],
                'batch_contract.py':(stack().native.e.ROOT/'batch_contract.py').read_text()}
            actual={}
            for name,text in expected.items():
                payload=await runtime.read(name,max_bytes=2*1024*1024)
                if payload!=text.encode():raise ValueError('canonical restart file mismatch: '+name)
                actual[name]=hashlib.sha256(payload).hexdigest()
            if setup_output:write(setup_output/(row['id']+'.json'),dict(coordinate=row,file_sha256=actual,started_epoch=started,ended_epoch=time.time(),fresh_native_runtime=runtime.name,old_kernel_restored=False,producer_replay=False))
    value=RestartTask(original.data,original.config)
    value.public_records=original.public_records;value.plain_query=goal;value.controller='free'
    return value

def verify():
    from protocol import digest
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('READY closure changed: '+path)
    return ready
