"""Bounded three-arm policy comparison, private immutable source adapters."""
import copy
import dataclasses
import hashlib
import importlib.util
import itertools
import json
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
UPTAKE=ROOT.parent/'root-receipt-uptake-v1'
DECISION=ROOT.parents[1]/'operations/2026-09-09-continuous-allocation/TYPED_CHILD_IMPLEMENTATION_DECISION.md'
DESIGN=ROOT.parents[1]/'ideas/2026-09-09-typed-helper-child-design.md'
IMAGE_READY=ROOT.parent/'runtime-preinstalled-image-v1/attempt-002/CPU_READY.json'
IMAGE='8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'
IMAGE_ROOT=IMAGE_READY.parent
ARMS=('unchanged','restored_raw','typed')
SEED_MASTER=981291600
ORDER_SEED=981291620
HEADER='x-typed-study-coordinate'

def checked_import(name,path,sha):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha: raise ValueError('pinned source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

u=checked_import('typed_frozen_uptake',UPTAKE/'experiment.py','29df4de005ac7157149a3cfdca7730f001e0f3d2f5a4661b1e7acca81ea2a104')
c,native,capture,old=u.c,u.native,u.capture,u.old
sys.path.insert(0,str(ROOT))
make_tasks,catalog_for,example_code=u.make_tasks,u.catalog_for,u.example_code

def with_prompt(task,arm):
    if arm not in ARMS: raise ValueError('unknown arm')
    return u.with_prompt(task,'restored_raw' if arm=='typed' else arm)

def binding_for(policy):
    original=c.read(UPTAKE/'SPEC.json')
    if policy!=original['policies']['step8']: raise ValueError('not fixed historical step8')
    binding=copy.deepcopy(original['bindings']['step8'])
    binding.pop('receipt_uptake_study',None)
    return {**binding,'typed_helper_study':ROOT.name,'decision_sha256':c.file_hash(DECISION)}

def build_plan(tasks):
    originals={r['task_name']:r for r in native.planned_rows('transfer-original') if r['repeat']==0}
    orders=list(itertools.permutations(ARMS))*2;random.Random(ORDER_SEED).shuffle(orders)
    plan=[]
    for i,name in enumerate(sorted(tasks)):
        source=originals[name]
        identity={k:source[k] for k in ('task_name','source_id','context_window_id','context_sha256')}
        identity.update(study=ROOT.name,weight='step8',phase='step8',split='transfer',repeat=0,
                        analysis_split='exposed_root_transfer_leaf_train_supported',seed=SEED_MASTER+i+1,temperature=.5,client_path='train')
        identity['matched_id']=c.digest(identity)
        for position,arm in enumerate(orders[i]):
            row={**identity,'arm':arm,'pair_id':identity['matched_id'],'pair_order':position,
                'group_id':c.digest([ROOT.name,name,arm]),'task_hash':with_prompt(tasks[name],arm).hash,'dispatch_order':len(plan)}
            row['id']=c.digest(row);plan.append(row)
    return plan

def make_context(endpoint,row):
    context=capture.make_context(endpoint,row)
    return dataclasses.replace(context,client=context.client.model_copy(update={'headers':{**context.client.headers,HEADER:row['id']}}))

def environment():
    value=copy.deepcopy(c.read(UPTAKE/'SPEC.json')['environment'])
    value['agent']['runtime']['image']=IMAGE
    return value

def collector():
    module=u.receipt.collector();module.IMAGE=IMAGE;module.IMAGE_ID='sha256:'+IMAGE
    return module

def verify():
    spec=c.read(ROOT/'SPEC.json');c.authenticate(spec['source_file_sha256'])
    if spec['plan']!=build_plan(make_tasks()) or spec['plan_sha256']!=c.digest(spec['plan']): raise ValueError('plan drift')
    return spec

def phase_spec(binding_path,endpoint_path,destination,cap):
    spec=copy.deepcopy(verify());binding,descriptor=c.read(binding_path),c.read(endpoint_path)
    if binding!=spec['bindings']['step8']: raise ValueError('wrong bound weights')
    # The unchanged descriptor check delegates only binding construction privately.
    prior=u.binding_for
    try:
        u.binding_for=binding_for;endpoint=u.validate_descriptor(descriptor,binding,binding_path)
    finally: u.binding_for=prior
    spec.update(endpoint=endpoint,role_binding=binding,binding_path=str(binding_path),endpoint_descriptor_path=str(endpoint_path),
        source_endpoint_descriptor=descriptor,wall_time_cap_seconds=min(1800,cap),parent_spec_sha256=c.file_hash(ROOT/'SPEC.json'),
        serving_evidence=capture.recursive.serving_evidence(Path(endpoint_path).parent/'inference.log'))
    spec['source_file_sha256'].update({str(p):c.file_hash(p) for p in (Path(binding_path),Path(endpoint_path),ROOT/'SPEC.json',ROOT/'READY.json')})
    c.write_once(destination,spec);return spec

def verify_phase(path):
    parent,actual=verify(),c.read(path);c.authenticate(actual['source_file_sha256'])
    for key in ('plan','plan_sha256','tasks','environment','image_id','bindings','max_concurrent_pairs'):
        if actual[key]!=parent[key]: raise ValueError('phase changed: '+key)
    if not 0<actual['wall_time_cap_seconds']<=1800 or actual['parent_spec_sha256']!=c.file_hash(ROOT/'SPEC.json'): raise ValueError('phase bounds drift')
    if actual['role_binding']!=parent['bindings']['step8']: raise ValueError('phase binding drift')
    capture.recursive.validate_serving_evidence(actual['serving_evidence'])
    return actual
