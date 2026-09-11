"""Exact96 CPU freeze and qualified two-alias component collection."""
import argparse
import ast
import asyncio
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import httpx
import study as s

ROOT=s.ROOT
path=s.padding.GRAMMAR/'driver.py'
if s.file_hash(path)!=s.padding.PINS[path]: raise ValueError('qualified HTTP helper changed')
loader=importlib.util.spec_from_file_location('agnews_private_http',path)
qualified_http=importlib.util.module_from_spec(loader);loader.loader.exec_module(qualified_http)
BASE,wire_hook=qualified_http.BASE,qualified_http.wire_hook
RUN_SOURCE=s.SIDE/'leaf-identity-counter-v1/driver.py'
RUN_SOURCE_SHA='f3c7bf409323d1854abfdb30efb64ead13c7a9de0dd6aadb5c64c7083e645580'
if s.file_hash(RUN_SOURCE)!=RUN_SOURCE_SHA: raise ValueError('qualified collector changed')
source=RUN_SOURCE.read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
source=ast.get_source_segment(source,node)
RUN_EDITS=[
    ('endpoint = s.read(endpoint_path)\n    qualified_http.validate_descriptor("old_sft", endpoint, spec["weight"])\n    if endpoint["model_alias"] != s.ALIAS:\n        raise ValueError("endpoint alias differs from all96 frozen requests")',
     'endpoints = validate_endpoints(endpoint_path, spec["weight"])\n    endpoint = endpoints["original"]',1),
    ('qualified_http.validate_live_models({"old_sft": endpoint}, response.json())','qualified_http.validate_live_models(endpoints, response.json())',1),
    ('"endpoint_sha256": s.file_hash(endpoint_path), "endpoint": endpoint,',
     '"endpoint_sha256": s.file_hash(endpoint_path), "endpoint": endpoint,\n        "endpoint_descriptors": endpoints, "endpoint_descriptor_sha256": {"original": s.file_hash(endpoint_path), "old_sft": s.file_hash(endpoint_path.with_name("endpoint-selected.json"))},',1),
    ('min(600,','min(900,',1)]
for before,after,count in RUN_EDITS:
    if source.count(before)!=count: raise ValueError('private run seam changed: '+before)
    source=source.replace(before,after)
RUN_ADAPTED_SHA256=hashlib.sha256(source.encode()).hexdigest()
exec(compile(source,str(RUN_SOURCE)+':AG96-private','exec'),globals())


def weights():
    binding=s.read(s.SIDE/'leaf-role-routing-v1/BOUND_WEIGHTS.json')
    models={};sources={}
    for weight,alias in s.ALIASES.items():
        value=binding['models'][alias]
        model={'path':value['path'],'model_sha256':value['adapter_sha256'],'config_sha256':value['config_sha256']}
        s.anchor.sst.authenticate_weight(weight,{'adapter':model,'base_model':BASE},sources)
        models[weight]=model
    return {'models':models,'base_model':BASE,'source_sha256':sources,
        'selection':'Exact original857a and existing historical validation-selected oldc32de; no AG outcome selection'}


def validate_endpoints(original_path,weight):
    paths={'original':Path(original_path),'old_sft':Path(original_path).with_name('endpoint-selected.json')}
    endpoints={name:s.read(path) for name,path in paths.items()}
    for name,endpoint in endpoints.items():
        qualified_http.validate_descriptor(name,endpoint,weight)
        if endpoint['model_alias']!=s.ALIASES[name]: raise ValueError('actual alias differs from frozen requests')
    for key in ('host','port','api_key_env','base_model'):
        if endpoints['original'][key]!=endpoints['old_sft'][key]: raise ValueError('weights not on same qualified service')
    return endpoints


def qualify(design,requests):
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(BASE['path'],local_files_only=True,trust_remote_code=False)
    grouping=deepcopy(design)
    for row in grouping['plan']: row['context_index']=row['context_index']*2+int(row['source_prefix']=='p')
    qualified=qualified_http.qualify(grouping,requests)
    ids={key:qualified_http.typed_prompt_ids(tokenizer,body) for key,body in requests.items()}
    proof=s.read(s.FEASIBILITY)
    checks={(c['context'],c['repeat'],c['prefix'],c['arm'],c['weight']):c for c in proof['checks']}
    triples=defaultdict(list)
    for row in design['plan']:
        key=(row['context_index'],row['repeat'],row['source_prefix'],row['arm'],row['weight'])
        body=requests[row['id']]
        if s.digest(ids[row['id']])!=checks[key]['typed_prompt_ids_sha256']:
            raise ValueError('approved candidate physical prompt changed: '+str(key))
        if s.digest(body)!=proof['body_identity_hashes']['/'.join(map(str,key))]:
            raise ValueError('approved candidate body changed: '+str(key))
        triples[key[:3]+(key[4],)].append(body)
    for bodies in triples.values():
        if len(bodies)!=3 or len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in bodies})!=1:
            raise ValueError('tag rules do not share displayed inputs')
        if any(b['messages'][0]!=bodies[0]['messages'][0] or b['tools']!=bodies[0]['tools'] for b in bodies):
            raise ValueError('tag-rule system/tools differ')
    for a,b in zip(design['plan'][::2],design['plan'][1::2],strict=True):
        x,y=requests[a['id']],requests[b['id']]
        if {k:v for k,v in x.items() if k!='model'}!={k:v for k,v in y.items() if k!='model'} or ids[a['id']]!=ids[b['id']]:
            raise ValueError('weight-only paired input changed')
    qualified.update(full_prompt_ids_sha256=s.digest(ids),weight_only_body_pairs=48,within_weight_tag_input_triples=32,
        exact_feasibility_request_crosswalk=96,max_prompt_plus_output=qualified['max_prompt_tokens']+3072)
    return qualified,ids


def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']: raise ValueError('immutable spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    data=s.read(ROOT/'DATA.json')
    if data!=s.build_data(): raise ValueError('frozen AG selection changed')
    expected=s.build_design(data)
    expected['rendered_prompts']=s.read(ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected!=spec['design'] or len(expected['plan'])!=96: raise ValueError('frozen AG96 plan changed')
    for row in expected['plan']:
        body=s.make_request(expected,row)
        if s.serialize(body)!=s.serialize(spec['requests'][row['id']]) or s.digest(body)!=spec['request_sha256'][row['id']]:
            raise ValueError('frozen body changed')


def seed_audit():
    paths=set()
    for sidecar in s.SIDE.iterdir():
        if not sidecar.is_dir() or sidecar==ROOT: continue
        for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
            paths.update(sidecar.glob(pattern))
    paths=sorted(p for p in paths if p.is_file())
    pattern=r'\b('+'|'.join(map(str,[s.MASTER,*s.SEEDS]))+r')\b'
    result=subprocess.run(['rg','-n',pattern,*map(str,paths)],capture_output=True,text=True,timeout=60)
    if result.returncode!=1 or result.stdout: raise ValueError('seed collision/audit failure: '+result.stdout[:1200])
    return {'master':s.MASTER,'sampling_seeds':s.SEEDS,'source_sha256':{str(p):s.file_hash(p) for p in paths},
        'exit_code':result.returncode,'matches':result.stdout,'scope':'Named top-level SPEC/READY/RECIPE/CAMPAIGN/SEED and one-level input PLAN JSON; excludes own sidecar, not global'}


def prepare():
    if (ROOT/'SPEC.json').exists(): raise ValueError('already frozen')
    audit=seed_audit();data=s.build_data();design=s.build_design(data)
    requests={r['id']:s.make_request(design,r) for r in design['plan']}
    qualified,ids=qualify(design,requests)
    design['rendered_prompts']=qualified['rendered_prompts']
    test=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_study.py','test_binding.py'],
        cwd=ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    if test.returncode: raise ValueError(test.stdout[-4000:]+test.stderr[-1000:])
    weight=weights()
    import owned
    values={'DATA.json':data,'CPU_QUALIFICATION.json':qualified,'PROMPT_IDS.json':ids,'SEED_AUDIT.json':audit,
        'WEIGHTS.json':weight,'DISPATCH.json':[{**row,'request_sha256':s.digest(requests[row['id']]),
            'typed_prompt_ids_sha256':s.digest(ids[row['id']])} for row in design['plan']],
        'SCHEMAS.json':{s.digest(b['structured_outputs']['json']):b['structured_outputs']['json'] for b in requests.values()},
        'CPU_TESTS.json':{'exit_code':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
            'red':'Five missing-study contract assertions and missing-owned assertion. Null fixture completed with actual started/ended/model_called fields; observed inherited first-error stop retained.',
            'gpu_calls':0,'network_model_calls':0,'fake_http_calls':13},
        'SOURCE_ADAPTERS.json':{'run_source_path':str(RUN_SOURCE),'run_source_sha256':RUN_SOURCE_SHA,'edits':RUN_EDITS,
            'run_adapted_sha256':RUN_ADAPTED_SHA256,'owned_adapted_sha256':owned.ADAPTED_SHA256,'owned_edits':owned.EDITS}}
    for name,value in values.items(): s.write_once(ROOT/name,value)
    sources=dict(s.read(s.PARENT/'SPEC.json')['source_sha256']);sources.update({str(p):h for p,h in s.PINS.items()})
    sources.update(weight['source_sha256']);sources.update({str(p):h for p,h in owned.PINNED.items()})
    sources[str(owned.SOURCE_PATH)]=owned.SOURCE_SHA256
    sources[str(owned.OBSERVER_PATH)]=owned.OBSERVER_SHA
    for artifact in data['source_provenance']['artifacts']: sources[artifact['path']]=artifact['sha256']
    sources[str(s.DECISION)]=s.file_hash(s.DECISION)
    sources.update({str(p):s.file_hash(p) for p in [*ROOT.glob('*.py'),*ROOT.glob('*.md'),*ROOT.glob('*.json')]})
    spec={'schema':ROOT.name,'design':design,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
        'source_sha256':sources,'weight':weight,'budget':{'calls':96,'workers':4,'collection_seconds':900,
            'work_seconds':1080,'owned_seconds':1200,'cleanup_seconds':120,'outer_seconds':1230,'timeout_seconds':120,'max_tokens':3072,'retries':0},
        'primary_alignment':'Displayed record only; no source numeric or permutation rescue',
        'frozen_before_model_calls':True,'underlying_data_license':'Unknown; research-use wording not a permissive license'}
    spec['spec_id']=s.digest(spec);s.write_once(ROOT/'SPEC.json',spec)
    verify(spec);owned.load_suite()
    ready={'status':'CPU_READY_PARENT_ACCEPTANCE_REQUIRED','planned_calls':96,'spec_id':spec['spec_id'],
        'spec_sha256':s.file_hash(ROOT/'SPEC.json'),'source_sha256':{**sources,str(ROOT/'SPEC.json'):s.file_hash(ROOT/'SPEC.json')},
        'launch_argv':[sys.executable,str(ROOT/'owned.py'),'--directory',str(ROOT/'owned/attempt-001')],
        'verify_argv':[sys.executable,str(ROOT/'owned.py'),'--verify'],'cwd':str(ROOT),
        'budget':spec['budget'],'qualified_schemas':qualified['schemas_compiled'],'max_input_plus_output':qualified['max_prompt_plus_output'],
        'weight_only_physical_pairs':48,'full_request_feasibility_matches':96,'tests_exit0':True,
        'preparation_gpu_calls':0,'preparation_model_calls':0,'environment':'Parent actual MIG UUID/LD/key inherited; no CUDA0 hardcoding',
        'source_review_report':str(ROOT/'SOURCE_REVIEW.md')}
    s.write_once(ROOT/'READY.json',ready)
    print(s.serialize({'ready_sha256':s.file_hash(ROOT/'READY.json'),'calls':96,'max_input_plus_output':ready['max_input_plus_output']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('prepare','verify','run'))
    parser.add_argument('--endpoint',type=Path);parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch',type=float);args=parser.parse_args()
    if args.command=='prepare': prepare()
    elif args.command=='verify': verify(s.read(ROOT/'SPEC.json'));print('verified')
    else:
        if not args.endpoint: parser.error('actual original endpoint required')
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(),args.output_dir.resolve(),args.overall_start_epoch)))
