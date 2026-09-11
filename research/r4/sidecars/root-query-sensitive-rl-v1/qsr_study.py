"""Unique namespace; immutable scientific and qualified runtime dependencies."""
import functools
from pathlib import Path
import sys
import importlib.util
import hashlib

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent
BOUNDED=SIDE/'root-bounded-refill-rl-v1';RUNTIME=SIDE/'runtime-an27-5780-v1'
ATTEMPT=ROOT/'outputs/attempt-001';MASTER=981381001;SEED=981381002
_spec=importlib.util.spec_from_file_location('qsr_qualified_bounded_study',BOUNDED/'study.py')
if hashlib.sha256((BOUNDED/'study.py').read_bytes()).hexdigest()!='c59ea132b47846108ccf4033c787782755214fce2f80d335d75407249144e83f':raise ValueError('bounded source changed')
bounded=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=bounded;_spec.loader.exec_module(bounded)
for _key in ('read','sha','digest','check','write','aliases','load','OLD','OLD_MANIFEST','PRIOR','LOCAL','CAMPAIGN','NATIVE','TRAIN','CHILD_SHA','PINS','fixed_start','prior_study'):
    globals()[_key]=getattr(bounded,_key)

def private(name,mapping):
    with aliases(mapping):return load('qsr_immutable_'+name[:-3],OLD/name,OLD_MANIFEST['source_sha256'][str(OLD/name)])
def data():return read(ROOT/'inputs/PUBLIC.json'),read(ROOT/'inputs/HOST_GOLD.json')
def candidate_plan(window):return read(ROOT/'inputs/PLANS.json')['training'][str(window)]
def endpoint_reward(reply,gold,completed,available):
    import re
    if not completed or not available or not isinstance(reply,str):return None
    match=re.fullmatch(r'Answer: ([0-9]+)',reply.strip());return int(bool(match and int(match[1])==gold))
def runtime():
    sys.path.insert(0,str(RUNTIME))
    import study_wrapper,lifecycle_adapter,credential_preflight
    study_wrapper.verify_runtime();lifecycle_adapter.verify();credential_preflight.require_provider_credential()
    return study_wrapper,lifecycle_adapter
@functools.lru_cache(maxsize=1)
def verify_prepared():
    value=read(ROOT/'CAMPAIGN.json')
    if digest({k:v for k,v in value.items() if k!='campaign_id'})!=value['campaign_id']:raise ValueError('campaign identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():check(path,pin)
    check(ROOT/'CAMPAIGN.json',read(ROOT/'READY.json')['campaign_sha256']);fixed_start()
    return value
def final_order():return tuple(sorted(('unchanged','trained'),key=lambda name:digest([MASTER,'final',name])))
