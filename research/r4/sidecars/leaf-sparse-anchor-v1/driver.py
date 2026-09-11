"""CPU freeze and parent-launched sparse144 via the qualified native run seam."""
import argparse
import ast
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import httpx
import study as s

ROOT=s.ROOT
HTTP_SOURCE=s.padding.GRAMMAR/'driver.py'
if s.file_hash(HTTP_SOURCE)!=s.padding.PINS[HTTP_SOURCE]: raise ValueError('qualified HTTP helper changed')
loader=importlib.util.spec_from_file_location('sparse_private_native_http',HTTP_SOURCE)
qualified_http=importlib.util.module_from_spec(loader);loader.loader.exec_module(qualified_http)
BASE=qualified_http.BASE
wire_hook=qualified_http.wire_hook
RUN_SOURCE=ROOT.parent/'leaf-identity-counter-v1/driver.py'
RUN_SOURCE_SHA='f3c7bf409323d1854abfdb30efb64ead13c7a9de0dd6aadb5c64c7083e645580'
if s.file_hash(RUN_SOURCE)!=RUN_SOURCE_SHA: raise ValueError('qualified collection source changed')
raw=RUN_SOURCE.read_text();tree=ast.parse(raw)
node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
source=ast.get_source_segment(raw,node)
RUN_EDITS=[('96','144',3),('min(600,','min(900,',1)]
for before,after,count in RUN_EDITS:
    if source.count(before)!=count: raise ValueError('run edit seam changed: '+before)
    source=source.replace(before,after)
RUN_ADAPTED_SHA256=hashlib.sha256(source.encode()).hexdigest()
exec(compile(source,str(RUN_SOURCE)+':sparse144-private','exec'),globals())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='weights')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(RUN_SOURCE)+':weights','exec'),globals())


def qualify(design,requests):
    import xgrammar as xgr
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(BASE['path'],local_files_only=True,trust_remote_code=False)
    config=s.read(Path(BASE['path'])/'config.json')
    compiler=xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(tokenizer,vocab_size=config['vocab_size']),max_threads=2,cache_enabled=True)
    ids={};prompts={};schemas={};checks=[]
    for row in design['plan']:
        key=row['id'];body=requests[key];schema=body['structured_outputs']['json'];sha=s.ordered_digest(schema)
        gold=design['batches'][row['batch_id']]['gold']
        sample=s.synthetic_output(gold,gold['labels'][0])
        if sha not in schemas:
            compiled=compiler.compile_json_schema(s.serialize(schema),any_whitespace=True)
            matcher=xgr.GrammarMatcher(compiled)
            if not matcher.accept_string(s.serialize(sample).encode()) or not matcher.is_completed(): raise ValueError('legal sparse schema fixture rejected')
            bad=deepcopy(sample);bad[0]={'label':sample[0]['label'],'tag':sample[0]['tag']}
            matcher=xgr.GrammarMatcher(compiled)
            if matcher.accept_string(s.serialize(bad).encode()) or matcher.is_completed(): raise ValueError('wrong anchor key order accepted')
            if row['cadence']>1:
                bad=deepcopy(sample);bad[1]={'label':gold['labels'][0]}
                matcher=xgr.GrammarMatcher(compiled)
                if matcher.accept_string(s.serialize(bad).encode()) or matcher.is_completed(): raise ValueError('nonanchor object accepted')
            schemas[sha]=True
        token_ids=qualified_http.typed_prompt_ids(tokenizer,body)
        if not token_ids or len(token_ids)+3072>8192: raise ValueError('complete prompt+3072 does not fit; no crop')
        ids[key]=token_ids
        prompts[key]={'tokens':len(token_ids),'typed_token_ids_sha256':s.digest(token_ids),
            'physical_source':'vLLM typed tools.model_dump and pinned native HF template'}
        synthetic={label:len(tokenizer.encode(s.serialize(s.synthetic_output(gold,label)),add_special_tokens=False)) for label in gold['labels']}
        checks.append(dict(coordinate_id=key,dataset=row['dataset'],cadence=row['cadence'],arm=row['arm'],
            anchors=len(row['anchor_positions']),prompt_tokens=len(token_ids),ordered_schema_sha256=sha,
            synthetic_canonical_label_output_tokens=synthetic,synthetic_labels_are_not_gold=True))
    if len(ids)!=144: raise ValueError('exact144 requests')
    for left,right in zip(design['plan'][::2],design['plan'][1::2],strict=True):
        a,b=requests[left['id']],requests[right['id']]
        if a['messages'][1]['content'].split(s.INPUT_MARKER)[1]!=b['messages'][1]['content'].split(s.INPUT_MARKER)[1]: raise ValueError('within-cadence input differs')
        if a['messages'][0]!=b['messages'][0] or a['tools']!=b['tools']: raise ValueError('system/tools differ')
        if [x['type'] for x in a['structured_outputs']['json']['prefixItems']]!=[x['type'] for x in b['structured_outputs']['json']['prefixItems']]: raise ValueError('within-cadence representation differs')
    return dict(requests=144,paired_visible_inputs=72,schemas_compiled=len(schemas),checks=checks,rendered_prompts=prompts,
        max_prompt_tokens=max(map(len,ids.values())),maximum_prompt_plus_output=max(map(len,ids.values()))+3072,
        synthetic_max_output_tokens=max(max(r['synthetic_canonical_label_output_tokens'].values()) for r in checks),
        synthetic_caution='Canonical repeated-label structure fixtures, not actual model output or a proof of arbitrary-output token maximum',
        versions={name:importlib.metadata.version(name) for name in ('vllm','xgrammar','transformers','tokenizers','httpx','pyarrow')},
        python=sys.version,gpu_calls=0,model_calls=0),ids


def seed_audit():
    paths=set()
    for child in s.SIDE.iterdir():
        if not child.is_dir() or child==ROOT: continue
        for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
            paths.update(p for p in child.glob(pattern) if p.is_file())
    paths=sorted(paths);pattern=r'\b('+'|'.join(map(str,[s.MASTER,*s.SEEDS]))+r')\b'
    result=subprocess.run(['rg','-n',pattern,*map(str,paths)],capture_output=True,text=True,timeout=60)
    if result.returncode!=1 or result.stdout: raise ValueError('seed collision/audit failure: '+result.stdout[:1000])
    return dict(master=s.MASTER,sampling_seeds=s.SEEDS,source_sha256={str(p):s.file_hash(p) for p in paths},
        exit_code=result.returncode,matches=result.stdout,scope='Named top-level ready/spec/recipe/campaign/seed and one-level inputs plans, own namespace excluded; not global')


def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']: raise ValueError('spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    if s.read(ROOT/'DATA.json')!=s.build_data(): raise ValueError('exposed source crosswalk changed')
    expected=s.build_design(s.read(ROOT/'DATA.json'));expected['rendered_prompts']=s.read(ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected!=spec['design'] or len(expected['plan'])!=144: raise ValueError('fixed design changed')
    for row in expected['plan']:
        body=s.make_request(expected,row);key=row['id']
        if s.serialize(body)!=s.serialize(spec['requests'][key]) or s.digest(body)!=spec['request_sha256'][key] or s.ordered_digest(body)!=spec['ordered_request_sha256'][key]: raise ValueError('frozen body/order changed')


def prepare():
    if (ROOT/'SPEC.json').exists() or (ROOT/'READY.json').exists(): raise ValueError('already frozen')
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='': raise ValueError('CPU prepare requires CUDA hidden')
    audit=seed_audit();data=s.build_data();design=s.build_design(data)
    requests={r['id']:s.make_request(design,r) for r in design['plan']}
    qualification,ids=qualify(design,requests);design['rendered_prompts']=qualification['rendered_prompts']
    print(s.serialize({'qualification_requests':144,'max_prompt':qualification['max_prompt_tokens'],
        'max_prompt_plus_output':qualification['maximum_prompt_plus_output'],'schemas':qualification['schemas_compiled']}),flush=True)
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_study.py','test_driver.py'],cwd=ROOT,
        capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    if tests.returncode: raise ValueError(tests.stdout[-4000:]+tests.stderr[-1000:])
    import owned
    weight=weights()
    values={'DATA.json':data,'DISPATCH.json':design['plan'],'REQUESTS.json':requests,'PROMPT_IDS.json':ids,
        'CPU_QUALIFICATION.json':qualification,'WEIGHTS.json':weight,'SEED_AUDIT.json':audit,
        'CPU_TESTS.json':dict(returncode=tests.returncode,stdout=tests.stdout,stderr=tests.stderr,
            red='Seven study tests and two driver tests failed missing-module before implementation',fake_http_calls=3,gpu_calls=0),
        'SOURCE_ADAPTERS.json':dict(run_source_path=str(RUN_SOURCE),run_source_sha256=RUN_SOURCE_SHA,run_edits=RUN_EDITS,
            run_adapted_sha256=RUN_ADAPTED_SHA256,owned_source_path=str(owned.SOURCE_PATH),owned_source_sha256=owned.SOURCE_SHA256,
            owned_edits=owned.EDITS,owned_adapted_sha256=owned.ADAPTED_SHA256,
            observer_path=str(owned.OBSERVER_PATH),observer_sha256=owned.OBSERVER_SHA)}
    for name,value in values.items(): s.write_once(ROOT/name,value)
    sources=dict(s.read(s.PARENT/'SPEC.json')['source_sha256']);sources.update(s.read(s.AG/'SPEC.json')['source_sha256'])
    sources.update({str(p):h for p,h in s.PINS.items()});sources.update(weight['source_sha256'])
    sources.update({str(p):h for p,h in owned.PINNED.items()})
    sources.update({str(owned.SOURCE_PATH):owned.SOURCE_SHA256,str(owned.OBSERVER_PATH):owned.OBSERVER_SHA,str(RUN_SOURCE):RUN_SOURCE_SHA})
    sources.update({str(p):s.file_hash(p) for p in [*ROOT.glob('*.py'),*ROOT.glob('*.md'),*ROOT.glob('*.json')]})
    spec=dict(schema=ROOT.name,design=design,requests=requests,request_sha256={k:s.digest(v) for k,v in requests.items()},
        ordered_request_sha256={k:s.ordered_digest(v) for k,v in requests.items()},
        source_sha256=sources,weight=weight,budget=dict(calls=144,collection_seconds=900,work_seconds=1080,
            owned_seconds=1200,cleanup_seconds=120,parent_seconds=1230,workers=4,request_timeout_seconds=120,max_tokens=3072,retries=0),
        frozen_before_model_calls=True,primary='Matching-minus-constant within cadence, tasks separate; accuracy/token Pareto across changed representations')
    spec['spec_id']=s.digest(spec);s.write_once(ROOT/'SPEC.json',spec)
    verify(spec);owned.load_suite()
    argv=[owned.PYTHON,str(ROOT/'owned.py'),'--directory',str(ROOT/'owned/attempt-001')]
    s.write_once(ROOT/'READY.json',dict(status='CPU_READY_PARENT_ACCEPTANCE_REQUIRED',calls=144,
        spec_sha256=s.file_hash(ROOT/'SPEC.json'),spec_id=spec['spec_id'],
        source_sha256={**sources,str(ROOT/'SPEC.json'):s.file_hash(ROOT/'SPEC.json')},
        launch_argv=argv,verify_argv=[owned.PYTHON,str(ROOT/'owned.py'),'--verify'],cwd=str(ROOT),
        budget=spec['budget'],output=str(ROOT/'outputs/attempt-001'),owned_directory=str(ROOT/'owned/attempt-001'),
        max_input_plus_output=qualification['maximum_prompt_plus_output'],schemas_compiled=qualification['schemas_compiled'],
        tests_exit0=True,gpu_calls=0,model_calls=0,
        authority='Parent only: exact predecessor/empty GPU/shared lock; wrapper owns only its authenticated service and releases in finally',
        environment='Pinned Prime Python, parent actual exclusive MIG UUID and LD_LIBRARY_PATH/API-key environment; no hardcoded CUDA0 or new install'))
    print(s.serialize({'ready_sha256':s.file_hash(ROOT/'READY.json'),'calls':144}),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','verify','run'])
    parser.add_argument('--endpoint',type=Path);parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch',type=float);args=parser.parse_args()
    if args.command=='prepare': prepare()
    elif args.command=='verify': verify(s.read(ROOT/'SPEC.json'));print('verified',flush=True)
    else:
        if not args.endpoint: parser.error('authenticated actual endpoint required')
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(),args.output_dir.resolve(),args.overall_start_epoch)))


if __name__=='__main__': main()
