"""Four frozen candidate windows and exact availability-fixed SFT8 start."""
import contextlib
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;OLD=SIDE/'root-adaptive-rlvr-v1'
MASTER=981316001;SEED=981316002
OLD_CAMPAIGN_SHA='51afee1b3753e5060955d205c1b923393f35af1550f23c4c536b12593c5fe4a1'
FINAL=SIDE/'root-success-trajectory-sft-v1/outputs/attempt-001/training'
FINAL_SHA='66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5'
STATE_SHA='506fc355e19b3201822ee1f6fb88eca1edd23e04219787b1d84484598f9531f2'
CONFIG_SHA='118bb737297c35d96a194b642026b1e58c72f945d55ae1616eb716cfc4601728'
def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def check(path,want):
    if sha(path)!=want:raise ValueError('authenticated source changed: '+str(path))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')
@contextlib.contextmanager
def aliases(mapping):
    before={k:sys.modules.get(k) for k in mapping};paths=list(sys.path);sys.modules.update(mapping)
    try:yield
    finally:
        sys.path[:]=paths
        for k,v in before.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
def load(name,path,want):
    check(path,want);sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
check(OLD/'CAMPAIGN.json',OLD_CAMPAIGN_SHA)
OLD_MANIFEST=read(OLD/'CAMPAIGN.json')
old=load('refill_old_study',OLD/'study.py',OLD_MANIFEST['source_sha256'][str(OLD/'study.py')])
for name in ('PRIOR','LOCAL','CAMPAIGN','NATIVE','TRAIN','CHILD_SHA','PINS','prior_study','data','endpoint_reward'):
    globals()[name]=getattr(old,name)
def private(name,mapping):
    with aliases(mapping):return load('refill_private_'+name[:-3],OLD/name,OLD_MANIFEST['source_sha256'][str(OLD/name)])

def build_plans(public):
    training=sorted((c for c in public if c['stratum']=='train'),key=lambda c:c['id'])
    if [len(c['records']) for c in training]!=[32]*4+[64]*4:raise ValueError('eight source training contexts changed')
    windows={}
    for window in range(1,5):
        i=window-1;small,big=training[i],training[i+4]
        pair=('single_user','global') if i%2==0 else ('global','single_user')
        groups=[]
        for group,(context,family) in enumerate(((small,pair[0]),(big,pair[1]),(small,pair[1]),(big,pair[0])),1):
            rows=[]
            for repeat in range(8):
                base=old.coordinate(context,family,repeat,981316101+i*32+(group-1)*8+repeat,'training')
                base.pop('id');base.update(candidate_window=window,candidate_group=group)
                rows.append({**base,'id':digest(base)})
            groups.append(rows)
        windows[str(window)]=groups
    original=old.build_plans(public);readout=[]
    for index,row in enumerate(original['validation']+original['transfer']):
        row={**row,'seed':981316501+index};row.pop('id');readout.append({**row,'id':digest(row)})
    return {'windows':windows,'readout':readout}

def candidate_plan(window):return [r for group in read(ROOT/'inputs/PLANS.json')['windows'][str(window)] for r in group]

@functools.lru_cache(maxsize=1)
def fixed_start():
    check(FINAL/'RESULT.json','d3279d748b618e0b50103e066c2680e1d3b59c1a13a37c36243d58812611a4a0')
    check(FINAL/'SELECTION.json','42b715969ca1d40faa08a82e261dd95c40499f339e24caf30678604ed4461f05')
    result=read(FINAL/'RESULT.json');chosen=read(FINAL/'SELECTION.json');path=FINAL/'checkpoint-0008'
    if result['selected']!=chosen or not result['complete'] or result['optimizer_steps']!=8 or chosen['step']!=8 or chosen['checkpoint']!=str(path):raise ValueError('not the fixed complete SFT8')
    check(path/'state.json',STATE_SHA);state=read(path/'state.json')
    if state['identity']!=result['identity'] or state['step']!=8 or state['files_sha256']!=result['files_sha256']:raise ValueError('SFT8 checkpoint identity differs')
    for name,want in state['files_sha256'].items():check(path/name,want)
    check(path/'adapter_model.safetensors',FINAL_SHA);check(path/'adapter_config.json',CONFIG_SHA)
    return {'step':0,'path':str(path),'adapter_sha256':FINAL_SHA,'config_sha256':CONFIG_SHA,
            'optimizer_sha256':None,'rng_sha256':None,'state_sha256':None}

@functools.lru_cache(maxsize=1)
def verify_prepared():
    m=read(ROOT/'CAMPAIGN.json')
    if digest({k:v for k,v in m.items() if k!='campaign_id'})!=m['campaign_id']:raise ValueError('campaign identity changed')
    for path,want in {**m['source_sha256'],**m['input_sha256']}.items():check(path,want)
    check(ROOT/'CAMPAIGN.json',read(ROOT/'READY.json')['campaign_sha256'])
    if read(ROOT/'inputs/PLANS.json')!=build_plans(data()[0]) or read(ROOT/'START.json')['policy']!=fixed_start():raise ValueError('frozen windows/start differ')
    return m
