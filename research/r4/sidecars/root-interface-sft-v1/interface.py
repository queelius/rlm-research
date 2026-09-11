"""Exact frozen typed batch matcher; common treatment for both roots, new source catalogs."""
import contextlib
import hashlib
import os
import sys
import study as s

ROOT=s.ROOT.parent/'typed-adaptive-operator-v1'
PINS={'experiment.py':'c9dfbcb398e60257b155557371dfc478aae2d714b4d48e8e14736501ce283013','contract.py':'f9e4e2fbe3e17f49a78c676c9691a97857f8c761b833e49504d0778b0eef2129','hooks.py':'ed1cc79ccd3ea11730916d42cb8dd1bc98ee052e9e6457a1fef0da03c65eca98','READY.json':'a7b4c072d1e815ce89f4316816a50b1139c270edb07efd8dca67e7cae12b43e4'}
for file,sha in PINS.items():s.check(ROOT/file,sha)
e=s.load('interface_typed_experiment',ROOT/'experiment.py',PINS['experiment.py'])
saved={k:sys.modules.get(k) for k in ('experiment','contract')}
try:
    sys.modules['experiment']=e
    contract=s.load('contract',ROOT/'contract.py',PINS['contract.py'])
    hooks=s.load('interface_exact_typed_hooks',ROOT/'hooks.py',PINS['hooks.py'])
finally:
    for k,v in saved.items():
        if v is None:sys.modules.pop(k,None)
        else:sys.modules[k]=v
    sys.path.insert(0,str(s.ROOT))

def catalogs(public):
    return {str(s.context_window_id(c)):{'context_sha256':hashlib.sha256(c['text'].encode()).hexdigest(),'records':c['records']} for c in public.values()}

@contextlib.contextmanager
def installed(binding,output,plan,public):
    hooks.configure_runtime()
    os.environ['VERIFIERS_CACHE_DIR']=str(output/'runtime-cache')
    with hooks.installed(binding,output,plan,catalogs(public)):yield
