"""Fixed broader data/task plans and pinned warm-start/runtime dependencies."""
import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent
BOUNDED=SIDE/'root-bounded-refill-rl-v1';DATA=SIDE/'root-curriculum-data-v1';RUNTIME=SIDE/'runtime-an27-5780-v1'
ATTEMPT=ROOT/'outputs/attempt-001';MASTER=981371001;SEED=981371002
def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def check(path,want):
    if sha(path)!=want:raise ValueError('pinned source changed '+str(path))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
@contextlib.contextmanager
def aliases(mapping):
    before={k:sys.modules.get(k) for k in mapping};paths=list(sys.path);sys.modules.update(mapping)
    try:yield
    finally:
        sys.path[:]=paths
        for k,v in before.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
def load(name,path,pin):
    check(path,pin);spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

bounded=load('broader_qualified_bounded_study',BOUNDED/'study.py','c59ea132b47846108ccf4033c787782755214fce2f80d335d75407249144e83f')
OLD,OLD_MANIFEST,PRIOR,LOCAL,CAMPAIGN,NATIVE,TRAIN,CHILD_SHA,PINS=(bounded.OLD,bounded.OLD_MANIFEST,bounded.PRIOR,bounded.LOCAL,bounded.CAMPAIGN,bounded.NATIVE,bounded.TRAIN,bounded.CHILD_SHA,bounded.PINS)
fixed_start=bounded.fixed_start;prior_study=bounded.prior_study
LABELS=('human being','numeric value','entity','location','description and abstract concept','abbreviation')

def private(name,mapping):
    with aliases(mapping):return load('broader_immutable_'+name[:-3],OLD/name,OLD_MANIFEST['source_sha256'][str(OLD/name)])

@functools.lru_cache(maxsize=1)
def verify_data():
    check(DATA/'MANIFEST.json','3b00b9a7ce4dd2cb086ed8937e459e852503139819d08c8e544d51f69c6bd0d6')
    manifest=read(DATA/'MANIFEST.json')
    for path,pin in {**manifest['source_sha256'],**manifest['files_sha256']}.items():check(path,pin)
    return manifest

def public_records(text):
    records=[]
    for line in text.splitlines():
        match=re.fullmatch(r'Date: ([^\r\n]+?) \|\| User: ([^\r\n]+?) \|\| Instance: ([^\r\n]+)',line)
        if not match:raise ValueError('not exact public Date/User/Instance line')
        records.append(dict(id=f'q{len(records)+1:04}',user=match[2],text=match[3]))
    if not records:raise ValueError('empty public context')
    return records

def data():
    verify_data();public=read(DATA/'PUBLIC.json');metadata={c['id']:c for c in read(DATA/'GROUPS.json')};gold=read(DATA/'HOST_GOLD.json');contexts=[];host={}
    for ci,c in enumerate(public['contexts']):
        m=metadata[c['id']]
        if m['split'] in ('transfer-sst','transfer-leaf-validation-exposed'):continue
        records=public_records(c['text'])
        if len(records)!=m['size']:raise ValueError('public row count differs')
        contexts.append({**c,'records':records,'size':m['size'],'stratum':m['split'],'source_partition':m['source_partition'],'group_ids':m['group_ids'],'native_context_id':98137200+ci})
        host[c['id']]={'answers':{t['id'].split(':')[1]:gold[t['id']]['answer_integer'] for t in public['tasks'] if t['context_id']==c['id']}}
    return contexts,host

def coordinate(context,task,repeat,seed,split,window=None):
    row=dict(context_id=context['id'],context_window_id=context['native_context_id'],task_name=task,family=task.split(':')[1],stratum=context['stratum'],split=split,repeat=repeat,seed=seed,records=context['size'],arm='typed',temperature=.5,client_path='train')
    if window is not None:row['candidate_window']=window
    row['id']=digest(row);return row

def build_plans(public):
    contexts={c['id']:c for c in public};plans={'training':{},'validation':[],'transfer':[]}
    for item in read(DATA/'CANDIDATE_SCHEDULE.json'):
        window=item['candidate_update'];rows=[]
        for group,task in enumerate(item['tasks']):
            for repeat in range(8):rows.append(coordinate(contexts[task.split(':')[0]],task,repeat,981371101+(window-1)*24+group*8+repeat,'training',window))
        plans['training'][str(window)]=rows
    validation=[c for c in public if c['stratum']=='validation']
    for i,c in enumerate(validation):
        label=LABELS[i%4].replace(' ','_')
        for repeat in range(2):plans['validation'].append(coordinate(c,c['id']+':'+label,repeat,981371601+len(plans['validation']),'validation'))
    for stratum in ('transfer-composition','transfer-size','transfer-leaf-test-exposed'):
        for i,c in enumerate(c for c in public if c['stratum']==stratum):
            labels=(LABELS[i%2],LABELS[4+i%2]) if stratum=='transfer-composition' else (LABELS[i%4],) if stratum=='transfer-size' else ('human being','numeric value')
            for label in labels:
                for repeat in range(2):plans['transfer'].append(coordinate(c,c['id']+':'+label.replace(' ','_'),repeat,981371701+len(plans['transfer']),stratum))
    return plans

def candidate_plan(window):return read(ROOT/'inputs/PLANS.json')['training'][str(window)]
def question(task_name):return next(t['question'] for t in read(DATA/'PUBLIC.json')['tasks'] if t['id']==task_name)
def endpoint_reward(reply,gold,completed,available):
    if not completed or not available or not isinstance(reply,str):return None
    match=re.fullmatch(r'Answer: ([0-9]+)',reply.strip());return int(bool(match and int(match[1])==gold))
def runtime():
    sys.path.insert(0,str(RUNTIME));import study_wrapper,lifecycle_adapter,credential_preflight
    study_wrapper.verify_runtime();lifecycle_adapter.verify();credential_preflight.require_provider_credential();return study_wrapper,lifecycle_adapter

@functools.lru_cache(maxsize=1)
def verify_prepared():
    value=read(ROOT/'CAMPAIGN.json')
    if digest({k:v for k,v in value.items() if k!='campaign_id'})!=value['campaign_id']:raise ValueError('campaign identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():check(path,pin)
    if sha(ROOT/'CAMPAIGN.json')!=read(ROOT/'READY.json')['campaign_sha256']:raise ValueError('READY campaign identity')
    return value

def final_order():return tuple(sorted(('unchanged','trained'),key=lambda name:digest([MASTER,'final',name])))
