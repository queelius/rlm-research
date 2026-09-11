"""Thin private adapters around authenticated plan-SFT/native/lifecycle code."""
import functools
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT=Path(__file__).resolve().parent
PLAN=ROOT.parent/'root-plan-sft-v1'
path=PLAN/'study.py'
if hashlib.sha256(path.read_bytes()).hexdigest()!='81776d6df5c65e7db3ee9891c9f59edc2a07f3cbabcc74209fdda8a0edc71a8a':raise ValueError('old plan source')
spec=importlib.util.spec_from_file_location('complete_frozen_plan',path);plan=importlib.util.module_from_spec(spec);sys.modules[spec.name]=plan;spec.loader.exec_module(plan)
for name in ('read','sha','check','write','digest','aliases','PRIOR','LOCAL','CONTROL','NATIVE','TRAIN','CHILD_SHA','BASE_SHA','START','START_SHA','LABELS'):
    globals()[name]=getattr(plan,name)
ARMS=('action_only','action_terminal');TRAIN_SEED=981330002

def private(name,path,pin,changes=None,extra=None):
    return plan.transformed(name,path,pin,changes or {},view=sys.modules[__name__],extra=extra)

@functools.lru_cache(maxsize=1)
def stack():
    st=plan.stack();view=ModuleType('complete_prior_view');view.__dict__.update(st.prior.__dict__)
    original_cid=st.prior.context_window_id
    def cid(c):return 98133000+int(c['id'].rsplit('-',1)[1])+(2 if c.get('helper_partition')=='validation' else 0) if c['id'].startswith('new-root-') else original_cid(c)
    view.context_window_id=cid;view.ROOT=ROOT
    native_path=PRIOR/'native.py';native_pin=read(PRIOR/'READY.json')['source_sha256'][str(native_path)]
    st.native=plan.transformed('complete_new_native_metadata',native_path,native_pin,
      {"'source_split':'new-root-disjoint-leaf-train-supported-'+context['stratum']":("'source_split':'root-disjoint-helper-'+context.get('helper_partition','train')",1)},view=view)
    st.prior=view;st.native.s=view;st.interface.s=view
    return st

def prior():return plan.prior()
def phase_order():return tuple(sorted(('unchanged',*ARMS),key=lambda a:digest(['981330001','readout',a])))
def training_order():return tuple(sorted(ARMS,key=lambda a:digest(['981330001','training',a])))

@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for p,h in {**ready['source_sha256'],**ready['input_sha256']}.items():check(p,h)
    return ready

def captured():
    directory=ROOT/'outputs/attempt-001/capture';manifest=read(directory/'CORPUS_READY.json')
    if manifest['prepared_identity']!=verify()['identity'] or manifest['episodes']!=16 or manifest['synthetic_child'] or manifest['sampled_root_policy']:
        raise ValueError('actual-child authored corpus required')
    for p,h in manifest['files_sha256'].items():check(p,h)
    episodes=read(directory/'EPISODES.json')
    original=read(PLAN/'prepared-v2/ROWS_canonical.json')
    if len(episodes)!=16:raise ValueError('all16 or stop')
    for e,action in zip(episodes,original):
        if e['episode_id']!=action['id'] or e['turns'][0]!=action or len(e['turns'])!=2:raise ValueError('unchanged canonical actions/order')
        for turn in e['turns']:
            if any(k in turn for k in ('old_logprobs','advantage','reward')):raise ValueError('no authored behavior likelihood')
    return episodes,sha(directory/'EPISODES.json'),manifest
