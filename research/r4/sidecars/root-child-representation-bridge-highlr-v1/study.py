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
sp=importlib.util.spec_from_file_location('highlr_bridge_original_study',p);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
for name in ('read','sha','digest','check','write','load','aliases','stack','PRIOR','NATIVE'):globals()[name]=getattr(old,name)
NEW_SHA='0ba42364183a311a8f5b67e4bac4e9294924c1dfb73f152a209811df09b78773'
CHECKPOINT=SIDE/'root-success-sft-lr-v1/outputs/attempt-001/training/checkpoint-0008'
NEW_CONFIG='a7804462e786cdf449fef943071ec12e37e2d83f7bde74a8faa322a7ed7449aa'

def binding():
    value=old.binding();value['models'][value['role_map']['root']]={'path':str(CHECKPOINT),'adapter_sha256':NEW_SHA,'config_sha256':NEW_CONFIG}
    return value

@functools.lru_cache(maxsize=1)
def adapter():
    b=load('highlr_original_bridge',OLD/'bridge.py',PINS['bridge.py'])
    with aliases({'study':old,'bridge':b}):
        c=load('highlr_original_contract',OLD/'contract.py',PINS['contract.py'])
        o=load('highlr_original_overlay',OLD/'overlay.py',PINS['overlay.py'])
        with aliases({'contract':c,'overlay':o}):return load('highlr_original_adapter',OLD/'adapter.py',PINS['adapter.py'])

def source(name):check(OLD/name,PINS[name]);return (OLD/name).read_text()

@functools.lru_cache(maxsize=1)
def verify():
    ready=read(ROOT/'READY.json')
    for p,h in ready['source_sha256'].items():check(p,h)
    spec=read(ROOT/'SPEC.json');previous=read(OLD/'SPEC.json')
    if spec['binding']!=binding() or {k:v for k,v in spec.items() if k!='binding'}!={k:v for k,v in previous.items() if k!='binding'}:raise ValueError('more than root binding changed')
    stack().local.validate_store();return spec
