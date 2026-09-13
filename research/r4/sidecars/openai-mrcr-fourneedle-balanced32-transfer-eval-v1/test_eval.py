import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import checkpoint,collect,study

def test_schedule_and_prefix_inventory():
    study.prepare_inputs(); rows=study.schedule(); assert len(rows)==32
    assert [r['seed'] for r in rows]==list(range(202609270000,202609270032))
    source={r['id']:r for r in study.records()}; assert {i:sum(source[r['record_id']]['requested_ordinal']==i for r in rows) for i in range(1,5)}=={1:8,2:8,3:8,4:8}
    prefixes=study.read(study.INPUTS/'PREFIXES.json');assert set(prefixes)=={r['id'] for r in rows};assert all(len(x['token_ids'])<=8192 for x in prefixes.values())

def test_actual_endpoint_bindings_and_child_match():
    checkpoint.verify_checkpoint();a=checkpoint.binding('cp32');b=checkpoint.binding('lr1e4')
    assert a['role_map']['root']!=b['role_map']['root'];assert a['fixed_child']==b['fixed_child'];assert a['models'][a['fixed_child']]==b['models'][b['fixed_child']]
    for x in (a,b):assert x['role_map']['children']==[x['fixed_child']]

def test_actual_collector_verifier_and_runtime_seams(tmp_path):
    ready={'schema':'test','inputs':{'schedule_sha256':study.digest(study.schedule())},'closure_sha256':{}}
    ready['identity']=study.digest(ready);path=tmp_path/'READY.json';path.write_text(json.dumps(ready))
    old=study.READY;study.READY=path
    try:
        assert collect.verify_ready()['identity']==ready['identity'];assert collect.source.verify_ready()['identity']==ready['identity']
        env=study.environment('long');assert len(env.taskset)==32
        for arm in ('cp32','lr1e4'):
            ctx=collect.source.model_context(Path('/tmp/not-contacted'),study.schedule()[0]);assert ctx is not None
    finally:study.READY=old
