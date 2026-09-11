"""Typed-only operator comparison over frozen adaptive tasks and programs."""
import ast
import copy
import contextlib
import dataclasses
import hashlib
import importlib.util
import itertools
import json
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'adaptive-filter-pilot-v1'
TYPED=ROOT.parent/'typed-helper-child-v1'
DESIGN=ROOT.parents[1]/'ideas/2026-09-09-typed-adaptive-operator-design.md'
SEEDS=(981292801,981292802)
ORDER_SEED=981292820
ARMS=('user_all','user_filter','global_shared')
HEADER='x-typed-study-coordinate'
IMAGE_READY=ROOT.parent/'runtime-preinstalled-image-v1/attempt-002/CPU_READY.json'
IMAGE_ROOT=IMAGE_READY.parent
IMAGE='8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'
def checked_import(name,path,sha):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha:raise ValueError('source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
a=checked_import('typed_adaptive_original',PRIOR/'experiment.py','ed7f94db1cb2d6b6ce30c4d78999fdc6b722f6195c39092429a029379f52e32d')
c,capture,native,old=a.c,a.capture,a.native,a.old
prior=a.prior
sys.path.insert(0,str(ROOT))
make_tasks,with_prompt=a.make_tasks,a.with_prompt

def binding_for(policy):
    binding=a.binding_for(policy);binding.pop('adaptive_filter_study',None)
    binding.update(typed_operator_study=ROOT.name,decision_sha256=c.file_hash(DESIGN));return binding

def environment_config():
    value=a.environment_config();value['agent']['runtime']['image']=IMAGE
    value['agent']['timeout']['setup']=120.
    return value

def make_context(endpoint,row):
    ctx=capture.make_context(endpoint,row)
    return dataclasses.replace(ctx,client=ctx.client.model_copy(update={'headers':{**ctx.client.headers,HEADER:row['id']}}))

def plan_for(contexts):
    physical,logical=[],[]
    orders=list(itertools.permutations(ARMS))+[ARMS,ARMS[::-1]];random.Random(ORDER_SEED).shuffle(orders)
    for context in contexts:
        for repeat,seed in enumerate(SEEDS):
            block=context['index']*2+repeat
            for position,job in enumerate(orders[block]):
                family=job.split('_')[0];controller='filter16' if job=='user_filter' else 'all16'
                name=f'adaptive-{context["index"]:02}-{family}'
                row={'study':ROOT.name,'block':block,'context_index':context['index'],'context_sha256':context['sha256'],
                    'context_window_id':1800+context['index'],'source_id':14800000+2*context['index']+(family=='global'),
                    'task_name':name,'job':job,'family':family,'controller':controller,'arm':job,'seed':seed,'repeat':repeat,
                    'temperature':.5,'client_path':'train','analysis_split':'exposed_original_adaptive_leaf_train_supported',
                    'pair_id':c.digest([ROOT.name,block]),'matched_id':c.digest([ROOT.name,block]),'pair_order':position,
                    'group_id':c.digest([ROOT.name,name,controller]),'dispatch_order':len(physical)}
                row['id']=c.digest(row);physical.append(row)
                for method in ('all16','filter16') if family=='global' else (controller,):
                    logical.append({'block':block,'context_index':context['index'],'seed':seed,'family':family,'method':method,'execution_id':row['id'],'shared_outcome':family=='global'})
    return physical,logical

def catalogs(contexts):return {str(1800+x['index']):{'context_sha256':x['sha256'],'records':x['records']} for x in contexts}

def collector_source():
    source=a.collector_source()
    for before,after in [('range(0, len(plan), 5)','range(0, len(plan), 3)'),('plan[offset : offset + 5]','plan[offset : offset + 3]')]:
        if source.count(before)!=1:raise ValueError('collector delta ambiguous')
        source=source.replace(before,after)
    return source

def collector():
    import types
    module=types.ModuleType('typed_operator_triples');module.__dict__.update(capture.base.__dict__)
    node=next(n for n in ast.parse(collector_source()).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(a.prior.COLLECTOR),'exec'),module.__dict__)
    module.IMAGE=IMAGE;module.IMAGE_ID='sha256:'+IMAGE;return module

def verify():
    spec=c.read(ROOT/'SPEC.json');c.authenticate(spec['source_file_sha256'])
    plan,logical=plan_for(c.read(PRIOR/'inputs/PUBLIC.json'))
    if plan!=spec['plan'] or logical!=spec['logical_cells'] or binding_for(spec['policy'])!=spec['binding']:raise ValueError('frozen plan/binding changed')
    if spec['environment']!=environment_config():raise ValueError('environment changed')
    return spec

@contextlib.contextmanager
def installed_hooks(binding,output):
    import hooks
    hooks.configure_runtime()
    with hooks.installed(binding,output,c.read(ROOT/'inputs/PLAN.json'),catalogs(c.read(PRIOR/'inputs/PUBLIC.json'))):yield
