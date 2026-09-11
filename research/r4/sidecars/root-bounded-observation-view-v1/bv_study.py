"""Isolated fixed24/c32 bounded-view factorial over the sealed accumulation runtime."""
import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
BASE=SIDE/'root-acquired-evidence-accumulation-v1';BASE_READY_SHA='ca0210997b73190f010ea56d7c40361ba6360e605f00d97b75f573364eb040a8'
NAMESPACE='bounded-observation-view-20260910-v1';SEEDS=tuple(range(981800101,981800109))

def raw_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
if raw_sha(BASE/'READY.json')!=BASE_READY_SHA:raise ValueError('sealed accumulation READY changed')
base_ready=json.loads((BASE/'READY.json').read_text());path=BASE/'ae_study.py'
if raw_sha(path)!=base_ready['source_sha256'][str(path)]:raise ValueError('sealed accumulation study changed')
spec=importlib.util.spec_from_file_location('bounded_view_frozen_accumulation',path);base=importlib.util.module_from_spec(spec);sys.modules[spec.name]=base;spec.loader.exec_module(base)
sha,read,write,digest,load,aliases=base.sha,base.read,base.write,base.digest,base.load,base.aliases
dose,NATIVE,OLD=base.dose,base.NATIVE,base.OLD
JOINT=base.JOINT
def __getattr__(name):return getattr(base,name)

@functools.lru_cache(maxsize=1)
def protocol():return base.protocol()

def make_task(context,row,gold):
    original=base.make_task(context,{**row,'accumulation_arm':row['return_arm']},gold)
    original_setup,original_finalize=original.setup,original.finalize
    async def setup(trace,runtime):
        await original_setup(trace,runtime)
        await runtime.write('.observation_view.json',json.dumps({'schema':'bounded-observation-view-config-v1','max_bytes':row['view_bytes']},sort_keys=True).encode())
    async def finalize(trace,runtime):
        # Harvest only after policy execution; the full analysis log never enters its history.
        try:
            raw=await runtime.read('.observation_view.jsonl',max_bytes=64*1024*1024)
            trace.info['bounded_observation_view']=dict(raw=raw.decode(),sha256=hashlib.sha256(raw).hexdigest(),policy_visibility='analysis-only harvest after rollout; policy saw only tool-message view')
        except Exception as error:
            trace.info['bounded_observation_view']=dict(raw=None,error_type=type(error).__name__,message=str(error))
        await original_finalize(trace,runtime)
    original.setup,original.finalize=setup,finalize
    original.data=original.data.model_copy(update={'source_split':'accumulation-exposed-bounded-view-factorial'})
    return original

@functools.lru_cache(maxsize=1)
def stack():
    native=base.stack().native;rows={r['id']:r for r in read(ROOT/'inputs/FREE_PLAN.json')}
    def task(context,prompt,gold,name):
        value=make_task(context,rows[name],gold)
        if value.data.prompt!=prompt:raise ValueError('bounded-view prompt changed')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))

def runtime():return base.runtime()
def selected():return base.selected()
def binding():
    value=base.binding();value['study']=ROOT.name;value['campaign_id']=ROOT.name
    value.pop('acquired_accumulation')
    value['bounded_observation_view']=dict(namespace=NAMESPACE,endpoints=32,blocks=8,return_arms=['B','C'],view_bytes=[4096,20000],no_training=True)
    return value
def validate(value,descriptor,path):
    if value!=binding():raise ValueError('bounded-view binding changed')
    j=base.o.joint();old=load('bounded_view_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original});old.validate_descriptor(value,descriptor,sha(path))

@functools.lru_cache(maxsize=1)
def interface(output):
    import bv_overlay
    original=base.interface(output);values={**vars(original)}
    original_installed=original.installed
    @contextlib.contextmanager
    def installed(binding,target,plan,public):
        from verifiers.v1.harnesses.rlm.harness import RLMHarness
        with original_installed(binding,target,plan,public):
            prior=RLMHarness.setup
            async def setup(self,runtime):
                await prior(self,runtime)
                result=await runtime.run(['python','-c',bv_overlay.overlay_program()],{})
                write(output/'bounded-view-overlays'/(__import__('uuid').uuid4().hex+'.json'),dict(runtime=runtime.name,program_sha256=digest(bv_overlay.overlay_program()),exit_code=result.exit_code,stdout=result.stdout,stderr=result.stderr))
                if result.exit_code:raise RuntimeError('bounded observation overlay failed')
            RLMHarness.setup=setup
            try:yield
            finally:RLMHarness.setup=prior
    values['installed']=installed
    return SimpleNamespace(**values)

def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('bounded-view identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():dose.check(path,pin)
    return ready
