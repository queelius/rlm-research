"""Exclusive CPU input preparation and source-pinned readiness; never launches science."""
import argparse
import ast
import os
from pathlib import Path
import subprocess
import time
import study as s
import protocol as p
def inputs():
    import native as n
    values=p.build();contexts={c['id']:c for c in values['PUBLIC.json']};expected={}
    for row in values['PLAN.json']:
        task=n.task(contexts[row['context_id']],values['QUERIES.json'][row['task_name']]['question'],row)
        expected[row['id']]=n.expected(task,row)
    for block in values['BLOCKS.json']:
        rows=[r for r in values['PLAN.json'] if r['block_id']==block['block_id']]
        if any(expected[r['id']]!=expected[rows[0]['id']] for r in rows):raise ValueError('paired native prefix differs')
    values['NATIVE_PREPARATION.json']=dict(expected=expected,root_max_tokens=2048,max_context_tokens=8192,all24_prefixes_verified=True,actual_runtime_fixture_required=True)
    receipt=s.read(s.SIDE.parent/'ideas/2026-09-09-root-warmstart-reference-feasibility.json')
    values['SOURCE_RECEIPT.json']=receipt
    seeds={r['seed'] for r in values['PLAN.json']};hits=[];files=[]
    for sidecar in sorted(s.SIDE.iterdir()):
        if not sidecar.is_dir() or sidecar==s.ROOT:continue
        for pattern in ('*PLAN*.json','*SEED*.json','inputs/*PLAN*.json','prepared/*PLAN*.json'):
            for path in sorted(sidecar.glob(pattern)):
                if str(path) in files:continue
                files.append(str(path))
                try:value=s.read(path)
                except (ValueError,UnicodeError):continue
                def walk(v):
                    if isinstance(v,dict):
                        if type(v.get('seed'))is int and v['seed'] in seeds:hits.append(dict(path=str(path),seed=v['seed']))
                        for child in v.values():walk(child)
                    elif isinstance(v,list):
                        for child in v:walk(child)
                walk(value)
    if hits:raise ValueError('proposed fresh namespace collides: '+str(hits))
    values['SEED_AUDIT.json']=dict(scope='top-level/inputs/prepared named PLAN/SEED JSON only; no global freshness claim',source_sha256={path:s.sha(path) for path in files},seeds=sorted(seeds),hits=hits)
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    print(dict(inputs=len(values),planned=24,max_prefix=max(len(v['token_ids']) for v in expected.values()),baseline=values['BASELINE_DISTRIBUTION.json']))
def qualify():
    command=[str(s.NATIVE),'-m','pytest','-q','test_protocol.py','test_entry.py','test_collect.py','test_native.py','test_lifecycle.py','test_collect_entry.py']
    before={str(path):s.sha(path) for path in s.ROOT.glob('*.py')};started=time.time()
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    if before!={str(path):s.sha(path) for path in s.ROOT.glob('*.py')}:raise ValueError('source changed during qualification')
    for path in s.ROOT.glob('*.py'):ast.parse(path.read_text())
    value=dict(passed=result.returncode==0,command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,source_sha256=before,elapsed_seconds=time.time()-started,gpu_calls=0,model_service_calls=0)
    s.write(s.ROOT/'CPU_TESTS.json',value)
    if result.returncode:raise ValueError('focused tests failed; preserved evidence')
    print(dict(passed=True,sha256=s.sha(s.ROOT/'CPU_TESTS.json')))
def seal():
    tests=s.read(s.ROOT/'CPU_TESTS.json');proof=s.read(s.ROOT/'qualification-native-001/RESULT.json')
    if not tests['passed'] or not proof['passed'] or proof['native_calls']!=3:raise ValueError('focused/native qualification required')
    for path,pin in {**tests['source_sha256'],**proof['source_sha256']}.items():s.check(path,pin)
    source=dict(s.read(s.QSR/'CAMPAIGN.json')['source_sha256']);source.update(s.read(s.SIDE/'root-fixed-policy-transfer-v1/READY.json')['source_sha256'])
    source.update(s.read(s.RUNTIME/'CPU_READY.json')['source_and_artifact_sha256']);source.update(s.read(s.RUNTIME/'LIFECYCLE_READY_V2.json')['source_sha256'])
    source.update({str(path):s.sha(path) for path in s.ROOT.glob('*') if path.is_file() and path.name!='READY.json'})
    source.update({str(path):s.sha(path) for path in (s.ROOT/'qualification-native-001').rglob('*.json')})
    inputs={str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')};inputs.update({str(s.QSR/'inputs'/name):pin for name,pin in s.INPUT_PINS.items()})
    for arm in s.ROOTS:
        for model in s.binding(arm)['models'].values():
            inputs[str(Path(model['path'])/'adapter_model.safetensors')]=model['adapter_sha256'];inputs[str(Path(model['path'])/'adapter_config.json')]=model['config_sha256']
    for path,pin in {**source,**inputs}.items():s.check(path,pin)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=inputs,planned=24,paired_blocks=8,context_clusters=4,roots=s.ROOTS,reference_label='released-weight reference served through zero-effect adapter; not bare-base transport',work_seconds=1650,owned_seconds=1770,outer_seconds=1800,phase_seconds=480,startup_seconds=180,collection_seconds=300,release_seconds=90,cleanup_seconds=120,outer_margin_seconds=30,episode_seconds=120,workers=4,root_action_max_tokens=2048,context_max_tokens=8192,child_adapter_sha256=s.CHILD_SHA,phase_order=p.phase_order(),argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],service_wrapper=str(s.RUNTIME/'service_wrapper_v2.py'),native_fixture=str(s.ROOT/'qualification-native-001/RESULT.json'),common_role='unchanged QSR native coding',root_grammar=False,optional_typed_children_unchanged=True,no_training=True,gpu_calls=0,model_service_calls=0,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    if s.verify()!=ready:raise ValueError('canonical write/read identity')
    print(dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json')))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('inputs','qualify','seal'));args=parser.parse_args();globals()[args.command]()
