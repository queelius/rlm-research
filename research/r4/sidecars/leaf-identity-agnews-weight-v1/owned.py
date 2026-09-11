"""Private exact96 dual-weight/cap adapter over qualified owned lifecycle."""
import ast
import hashlib
from pathlib import Path

SOURCE_PATH=Path(__file__).resolve().parent.parent/'leaf-identity-counter-v1/owned.py'
SOURCE_SHA256='8b3f18ec32748ba5189a61d64aea99c5ce087b15b53ae999e643c60e48261d29'
OBSERVER_PATH=SOURCE_PATH.parent.parent/'root-seed-lifecycle-continuation-v1/driver.py'
OBSERVER_SHA='bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd'
if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()!=SOURCE_SHA256: raise ValueError('owned source changed')
source=SOURCE_PATH.read_text()
EDITS=[('identity_counter','agnews_weight',5),('630','930',1),('600','900',1),
    ('"service_model_count": 1','"service_model_count": 2',1),
    ('if __name__ == "__main__":','if False:',1)]
for before,after,count in EDITS:
    if source.count(before)!=count: raise ValueError('owned adapter count changed: '+before)
    source=source.replace(before,after)
ADAPTED_SHA256=hashlib.sha256(source.encode()).hexdigest()
exec(compile(source,str(SOURCE_PATH)+':AG96-private','exec'),globals())
_load_suite=load_suite


def load_suite():
    suite=_load_suite()
    if sha(OBSERVER_PATH)!=OBSERVER_SHA: raise ValueError('qualified process-absence helper changed')
    node=next(n for n in ast.parse(OBSERVER_PATH.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='observe_or_absent')
    scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(OBSERVER_PATH),'exec'),scope)
    original=suite.life.v1.process_identity
    suite.life.v1.process_identity=lambda pid:scope['observe_or_absent'](original,pid)
    return suite


def service_binding(weights,weights_path,weights_sha):
    import study as s
    return {'schema':'agnews-fixed-original-old-dual-adapter-binding-v1',
        'models':{s.ALIASES[name]:{'path':m['path'],'adapter_sha256':m['model_sha256'],'config_sha256':m['config_sha256']}
            for name,m in weights['models'].items()},
        'role_map':{'root':s.ALIASES['original'],'children':[s.ALIASES['old_sft']]},
        'selection_path':str(weights_path),'selection_sha256':weights_sha,
        'selection_semantics':'Fixed original857a and historical oldc32de; no AG outcome-based weight choice',
        'post_training_test_consulted_for_binding':False}


if __name__=='__main__': main()
