"""CPU preparation only; exclusive manifests, focused proofs and canonical seal."""
import argparse
import ast
import json
import os
import subprocess
import time
import study as s
import protocol as p

def inputs():
    import native as n
    import collect as c
    values=p.build();binding=s.binding()
    values['BINDING.json']=binding
    by_context={v['id']:v for v in values['PUBLIC.json']}
    values['ACQUISITION_REQUESTS.json']={r['id']:c.extraction_request(by_context[r['context_id']],r,binding) for r in values['ACQUISITION_PLAN.json']}
    tokenizer=s.qnative().stack().native.renderer()._tokenizer;checks=[]
    for row in values['PLAN.json']:
        context=by_context[row['context_id']];query=values['QUERIES.json'][row['task_name']]['question']
        # Largest canonical label fixture tests input budget only; never a scientific map.
        map_raw=json.dumps({r['id']:'description and abstract concept' for r in context['records']},indent=2) if row['evidence']=='map' else None
        task=n.task(context,query,row,map_raw);expected=n.expected(task,row)
        checks.append(dict(id=row['id'],role=row['role'],evidence=row['evidence'],prefix_length=len(expected['token_ids']),prefix_token_sha256=s.digest(expected['token_ids']),cpu_map_fixture_only=True,root_max_tokens=2048))
    acquisition_checks=[]
    for identifier,body in values['ACQUISITION_REQUESTS.json'].items():
        ids=tokenizer.apply_chat_template(body['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False,return_dict=False)
        if len(ids)+1536>8192:raise ValueError('source context budget')
        acquisition_checks.append(dict(id=identifier,prompt_token_ids=ids,prompt_tokens=len(ids),max_tokens=1536))
    values['NATIVE_PREPARATION.json']=dict(root_checks=checks,acquisition_checks=acquisition_checks,actual_map_prompts_frozen_only_after_acquisition=True,root_original_sampling=dict(max_tokens=2048,temperature=.5,top_p=1.,top_k=-1,min_p=0.),root_tools_and_optional_typed_children_unchanged=True)
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    print(dict(inputs=len(values),roots=24,acquisitions=2,max_fixture_prefix=max(v['prefix_length'] for v in checks)))
def qualify():
    command=[str(s.NATIVE),'-m','pytest','-q','test_protocol.py','test_native.py','test_collect.py','test_entry.py','test_lifecycle.py','test_collect_entry.py']
    before={str(path):s.sha(path) for path in s.ROOT.glob('*.py')};started=time.time()
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    if before!={str(path):s.sha(path) for path in s.ROOT.glob('*.py')}:raise ValueError('source changed during qualification')
    for path in s.ROOT.glob('*.py'):ast.parse(path.read_text())
    value=dict(passed=result.returncode==0,command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,source_sha256=before,elapsed_seconds=time.time()-started,gpu_calls=0,model_service_calls=0)
    s.write(s.ROOT/'CPU_TESTS_FINAL_V2.json',value)
    if result.returncode:raise ValueError('focused tests failed; artifact retained')
    print(dict(passed=True,sha256=s.sha(s.ROOT/'CPU_TESTS_FINAL_V2.json')))
def seal():
    tests=s.read(s.ROOT/'CPU_TESTS_FINAL_V2.json');proof=s.read(s.ROOT/'qualification-native-002/RESULT.json')
    if not tests['passed'] or not proof['passed'] or proof['native_calls']!=12:raise ValueError('fresh focused/native qualification required')
    for path,pin in {**tests['source_sha256'],**proof['source_sha256']}.items():s.check(path,pin)
    source=dict(s.read(s.QSR/'CAMPAIGN.json')['source_sha256'])
    transfer=s.read(s.SIDE/'root-fixed-policy-transfer-v1/READY.json')
    # Reuse immutable qualified lifecycle ancestry, not any live transfer outcomes.
    source.update(transfer['source_sha256'])
    source.update(s.read(s.RUNTIME/'CPU_READY.json')['source_and_artifact_sha256'])
    source.update(s.read(s.RUNTIME/'LIFECYCLE_READY_V2.json')['source_sha256'])
    source.update({str(path):s.sha(path) for path in s.ROOT.glob('*') if path.is_file() and path.name!='READY.json'})
    source.update({str(path):s.sha(path) for directory in ('qualification-native-001','qualification-native-002') for path in (s.ROOT/directory).rglob('*.json')})
    import native as n
    source[str(n.role().NANO_SOURCE)]=n.role().NANO_SHA
    inputs={str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')}
    inputs.update({str(s.QSR/'inputs'/name):pin for name,pin in s.INPUT_PINS.items()})
    for model in s.binding()['models'].values():
        inputs[str(__import__('pathlib').Path(model['path'])/'adapter_model.safetensors')]=model['adapter_sha256'];inputs[str(__import__('pathlib').Path(model['path'])/'adapter_config.json')]=model['config_sha256']
    for path,pin in {**source,**inputs}.items():s.check(path,pin)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256=inputs,planned_roots=24,planned_source_acquisitions=2,context_clusters=2,work_seconds=1080,owned_seconds=1170,outer_seconds=1200,cleanup_seconds=90,outer_margin_seconds=30,episode_seconds=120,workers=4,acquisition_seconds=150,root_action_max_tokens=2048,context_max_tokens=8192,root_adapter_sha256=s.binding()['models'][s.binding()['role_map']['root']]['adapter_sha256'],child_adapter_sha256=s.CHILD_SHA,base_manifest_sha256='19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f',argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],service_wrapper=str(s.RUNTIME/'service_wrapper_v2.py'),native_fixture=str(s.ROOT/'qualification-native-002/RESULT.json'),source_gate='structurally complete actual c32 map only; semantic errors preserved',common_all_scope_wording_changed=True,root_and_acquisition_grammar=False,optional_native_typed_children_unchanged=True,gpu_calls=0,model_service_calls=0,provider_billing=None,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    if s.verify()!=ready:raise ValueError('write/read identity regression')
    print(dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json')))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));args=ap.parse_args();globals()[args.command]()
