"""One72-call study; unchanged original qualified service launcher and ownership."""
import ast
import hashlib
from pathlib import Path

SOURCE_PATH=Path(__file__).resolve().parent.parent/'leaf-identity-counter-v1/owned.py'
SOURCE_SHA256='8b3f18ec32748ba5189a61d64aea99c5ce087b15b53ae999e643c60e48261d29'
OBSERVER_PATH=SOURCE_PATH.parent.parent/'root-seed-lifecycle-continuation-v1/driver.py'
OBSERVER_SHA='bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd'
if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()!=SOURCE_SHA256:raise ValueError('owned source changed')
source=SOURCE_PATH.read_text()
EDITS=[('identity_counter','shifted_cue',5),('96','72',2),('1080','750',1),('1200','870',3),
       ('if __name__ == "__main__":','if False:',1)]
for before,after,count in EDITS:
    if source.count(before)!=count:raise ValueError('owned seam count changed: '+before)
    source=source.replace(before,after)
ADAPTED_SHA256=hashlib.sha256(source.encode()).hexdigest()
exec(compile(source,str(SOURCE_PATH)+':shifted72-private','exec'),globals())
_load_suite=load_suite
def load_suite():
    suite=_load_suite()
    # The legacy suite prepends its own helper paths; keep this study's CLI imports local.
    sys.path.insert(0,str(ROOT))
    if sha(OBSERVER_PATH)!=OBSERVER_SHA:raise ValueError('process-absence helper changed')
    node=next(n for n in ast.parse(OBSERVER_PATH.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='observe_or_absent')
    scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(OBSERVER_PATH),'exec'),scope)
    original=suite.life.v1.process_identity
    suite.life.v1.process_identity=lambda pid:scope['observe_or_absent'](original,pid)
    if suite.SERVE!=suite.c.ROLE/'source/serve.py':raise ValueError('actual launcher/root mismatch')
    return suite
if __name__=='__main__':main()
