"""Fixed BA18 base/cp1 native readout; no source or outcome selection."""
import copy
import functools
import importlib.util
from pathlib import Path
import types

ROOT=Path(__file__).resolve().parent;TRAIN=ROOT.parent/'b05-flat-selection-rl-v1'
spec=importlib.util.spec_from_file_location('ba18_eval_training',TRAIN/'study.py')
train=importlib.util.module_from_spec(spec);spec.loader.exec_module(train)
for name in ('sha','read','digest','write_x','bytes_x','load','aliases'):globals()[name]=getattr(train,name)
source=train.width.source;SOURCE=train.width.SOURCE
now=train.width.now;tokenizer=train.width.tokenizer;NATIVE=train.NATIVE
RUNTIME=ROOT.parent/'runtime-an22-5801-v1';READY=ROOT/'READY.json';ATTEMPT=ROOT/'outputs/attempt-001'
MAX_PHYSICAL=72;CONCURRENCY=4;SCIENCE_SECONDS=600;OWNER_SECONDS=700;EXTERNAL_SECONDS=800

@functools.lru_cache(None)
def tasks():return read(TRAIN/'EVAL_TASKS.json')['tasks']

def task(call):
    return next(t for t in tasks() if (t['split'],t['root_id'],t['repeat'])==(call['split'],call['root_id'],call['repeat']))

@functools.lru_cache(None)
def active_roots():
    return [dict(root_id=t['root_id'],split=t['split'],width=t['width']) for t in tasks() if t['repeat']==0]

@functools.lru_cache(None)
def calls():
    result=[]
    for i,root in enumerate(active_roots()):
        for repeat in range(2):
            arms=('base','cp1') if (i+repeat)%2==0 else ('cp1','base')
            for arm in arms:
                t=next(t for t in tasks() if t['root_id']==root['root_id'] and t['repeat']==repeat)
                result.append(dict(**root,repeat=repeat,arm=arm,kind='child',seed=t['seed'],max_tokens=384))
    return result

def call_id(c):return f"{c['split']}-{c['root_id']}-r{c['repeat']}-{c['arm']}"
def prompt(c):return task(c)['prompt']
def request_for(c):
    value=copy.deepcopy(task(c)['request']);value['model']=str(train.BASE) if c['arm']=='base' else train.ALIAS
    return value

def decode_response(body,response):
    assert body['model'] in (str(train.BASE),train.ALIAS)
    fn=source.decode_response;scope={**fn.__globals__,'MODEL_ALIAS':body['model']}
    return types.FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)(body,response)

@functools.lru_cache(None)
def b05():
    with aliases({'study':train.width},train.WIDTH):return load('ba18_eval_ID_contract',train.WIDTH/'interface.py')

def child(c):
    if c['split']=='train':
        old=next(x for x in train.width.calls() if x['root_id']==c['root_id'] and x['helpers']==1)
        return train.width.child(old)
    root=next(r for r in read(TRAIN/'HELD_PUBLIC.json')['roots'] if r['root_id']==c['root_id'])
    return source.b05().extract_child(root['safe_root'],root['selected_stage'])

def gold():return {(r['split'],r['root_id']):set(r['gold_ids']) for r in read(TRAIN/'HOST_GOLD.json')['rows']}

def checkpoint():
    with aliases({'study':train},TRAIN):
        core=load('ba18_eval_training_core',TRAIN/'core.py')
        with aliases({'core':core},TRAIN):return load('ba18_eval_checkpoint',TRAIN/'checkpoint.py').endpoint()

def binding():
    q=read(ROOT/'CHECKPOINT_QUALIFICATION.json');b=q['binding'];assert q['eligible']
    return dict(schema='BA18-fixed-step1-native-service-binding-v1',
        selection_path=str(ROOT/'CHECKPOINT_QUALIFICATION.json'),selection_sha256=sha(ROOT/'CHECKPOINT_QUALIFICATION.json'),
        selection='sole fixed step1, no accuracy qualification',
        models={train.ALIAS:dict(path=q['checkpoint'],adapter_sha256=b['adapter_sha256'],config_sha256=b['adapter_config_sha256'])},
        role_map={'root':train.ALIAS,'children':[train.ALIAS]},
        actual_released_base_model=str(train.BASE),base_control_adapter=None)

def dependencies():
    suite=load('ba18_eval_current_suite',ROOT.parent/'leaf-post-sft-suite-v1/suite.py');suite.verify()
    with aliases({},RUNTIME):
        runtime=load('ba18_eval_runtime',RUNTIME/'study_wrapper.py')
        with aliases({'study_wrapper':runtime},RUNTIME):
            lifecycle=load('ba18_eval_lifecycle',RUNTIME/'lifecycle_adapter.py')
    runtime.verify_runtime();lifecycle.install(suite)
    assert suite.SERVE==RUNTIME/'service_wrapper_v2.py' and suite.life.ALLOCATION_SERVICE==suite.SERVE
    return suite

def verify():
    ready=read(READY);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for p,h in ready['closure_sha256'].items():assert sha(p)==h,p
    assert len(calls())==72 and len(active_roots())==18 and len({call_id(c) for c in calls()})==72
    assert read(ROOT/'INPUTS.json')['calls']==[dict(call=c,request=request_for(c),prompt=prompt(c)) for c in calls()]
    for c in calls():assert len(request_for(c)['token_ids'])+384<=8192
    assert binding()==read(ROOT/'BINDING.json')
    dependencies();return ready
