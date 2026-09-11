"""Only root binding changes; immutable source/input reuse, no policy outcome selection."""
import functools
import hashlib
import importlib.util
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;OLD=SIDE/'root-child-representation-bridge-v1'
PINS={'study.py':'27fb88eaf264f655a56ee4ae9be747195f1143f6a4d4c977bbba8ef8f69662b0',
 'driver.py':'8c53878be27e812b1548f61b767426966e9a94125c5b8b5d866ece7ef2086345',
 'collect.py':'04af5de172e54697111e6f09d4d1901eb1312cfe632c21279e02ea33e1501c2e',
 'adapter.py':'e556214c116c1757d7168416953c65ad49734a27f3ffc5784ee8183f0af71e1a',
 'bridge.py':'d785c84eadd14e5105d5e6a53940e699043b25f066d54cf43f43e7f1fa7377d5',
 'contract.py':'fd4777c6b516d2bb3d6550abf516a4efc3fdd0167b993db0dcc18fe2ad458fee',
 'overlay.py':'69d5355a3754d3331e2b0eb5e6883a092f1d7963b5945e08583e1c455395c276'}
p=OLD/'study.py'
if hashlib.sha256(p.read_bytes()).hexdigest()!=PINS['study.py']:raise ValueError('frozen bridge source changed')
sp=importlib.util.spec_from_file_location('rl4_bridge_original_study',p);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
for name in ('read','sha','digest','check','write','load','aliases','stack','PRIOR','NATIVE'):globals()[name]=getattr(old,name)
NEW_SHA='2286be3f7c0c9cc0e22c8ef8e3473b7d8eb6ec4b7a789ca380a0af9d3b944c71'
CHECKPOINT=SIDE/'root-bounded-refill-rl-v1/outputs/attempt-001/window-04/training/checkpoint-4'
NEW_CONFIG='040408bf8d0ca5fc5d42e0725f8d392849388836d3e3b7d9c372f1b2b3e49377'

def binding():
    value=old.binding();value['models'][value['role_map']['root']]={'path':str(CHECKPOINT),'adapter_sha256':NEW_SHA,'config_sha256':NEW_CONFIG}
    return value

@functools.lru_cache(maxsize=1)
def adapter():
    b=load('rl4_original_bridge',OLD/'bridge.py',PINS['bridge.py'])
    with aliases({'study':old,'bridge':b}):
        c=load('rl4_original_contract',OLD/'contract.py',PINS['contract.py'])
        o=load('rl4_original_overlay',OLD/'overlay.py',PINS['overlay.py'])
        with aliases({'contract':c,'overlay':o}):return load('rl4_original_adapter',OLD/'adapter.py',PINS['adapter.py'])

def source(name):check(OLD/name,PINS[name]);return (OLD/name).read_text()

@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    for p,h in ready['source_sha256'].items():check(p,h)
    spec=read(ROOT/'SPEC.json');previous=read(OLD/'SPEC.json')
    if spec['binding']!=binding() or {k:v for k,v in spec.items() if k!='binding'}!={k:v for k,v in previous.items() if k!='binding'}:raise ValueError('more than root binding changed')
    stack().local.validate_store();return spec
