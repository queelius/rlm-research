"""Freeze48 ordered decoder contracts; parent-launched qualified leaf collection."""
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
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import httpx
import study as s

ROOT=s.ROOT
HTTP_SOURCE=s.padding.GRAMMAR/'driver.py'
if s.file_hash(HTTP_SOURCE)!=s.padding.PINS[HTTP_SOURCE]: raise ValueError('qualified HTTP helper changed')
loader=importlib.util.spec_from_file_location('cue_order_private_http',HTTP_SOURCE)
qualified_http=importlib.util.module_from_spec(loader);loader.loader.exec_module(qualified_http)
BASE=qualified_http.BASE
RUN_SOURCE=s.SIDE/'leaf-identity-counter-v1/driver.py'
RUN_SOURCE_SHA='f3c7bf409323d1854abfdb30efb64ead13c7a9de0dd6aadb5c64c7083e645580'
if s.file_hash(RUN_SOURCE)!=RUN_SOURCE_SHA: raise ValueError('qualified collector changed')
raw=RUN_SOURCE.read_text();tree=ast.parse(raw)
node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
source=ast.get_source_segment(raw,node)
RUN_EDITS=[('96','48',3),('1080','780',2),('launch + 1200','launch + 900',1)]
for before,after,count in RUN_EDITS:
    if source.count(before)!=count: raise ValueError('private run seam changed: '+before)
    source=source.replace(before,after)
RUN_ADAPTED_SHA256=hashlib.sha256(source.encode()).hexdigest()
exec(compile(source,str(RUN_SOURCE)+':cue48-private','exec'),globals())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='weights')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(RUN_SOURCE)+':weights','exec'),globals())


def wire_hook(spec,output):
    # Never use sorted-key identities to resolve field-order conditions.
    by_hash={sha:key for key,sha in spec['ordered_request_sha256'].items()}
    if len(by_hash)!=len(spec['requests']): raise ValueError('duplicate ordered request identity')
    async def capture(request):
        if request.method!='POST' or not request.url.path.endswith('/chat/completions'): return
        sha=hashlib.sha256(request.content).hexdigest()
        key=by_hash.get(sha)
        if key is None or request.content!=s.serialize(spec['requests'][key]).encode():
            raise ValueError('actual ordered wire body differs from frozen request')
        s.write_once(output/'wire'/f'{key}.json',{'coordinate_id':key,'route':request.url.path,
            'body_utf8':request.content.decode(),'body_sha256':sha,
            'ordered_schema_sha256':s.ordered_digest(spec['requests'][key]['structured_outputs']['json']),
            'credentials_recorded':False})
    return capture


def qualify(design,requests):
    import xgrammar as xgr
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(BASE['path'],local_files_only=True,trust_remote_code=False)
    config=s.read(Path(BASE['path'])/'config.json')
    compiler=xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(tokenizer,vocab_size=config['vocab_size']),max_threads=2,cache_enabled=True)
    proof=s.read(s.FEASIBILITY)
    old={(c['context_index'],c['arm'],c['seed'],tuple(c['order'])):c for c in proof['checks']}
    checks=[];ids={};prompts={};schemas={};paired=defaultdict(list)
    for row in design['plan']:
        body=requests[row['id']];schema=body['structured_outputs']['json'];order=s.ORDERS[row['field_order']]
        serialized=s.serialize(schema);schema_sha=s.ordered_digest(schema)
        if schema_sha not in schemas:
            schemas[schema_sha]=compiler.compile_json_schema(serialized,any_whitespace=True)
        compiled=schemas[schema_sha]
        values=[{'tag':item['properties']['tag']['const'],'label':item['properties']['label']['enum'][0]} for item in schema['prefixItems']]
        sample=[{key:v[key] for key in order} for v in values]
        opposite=[{key:v[key] for key in reversed(order)} for v in values]
        matcher=xgr.GrammarMatcher(compiled)
        if not matcher.accept_string(s.serialize(sample).encode()) or not matcher.is_completed(): raise ValueError('assigned grammar order not accepted')
        matcher=xgr.GrammarMatcher(compiled)
        if matcher.accept_string(s.serialize(opposite).encode()) or matcher.is_completed(): raise ValueError('opposite grammar order accepted; do not launch')
        token_ids=qualified_http.typed_prompt_ids(tokenizer,body)
        if not token_ids or len(token_ids)+3072>8192: raise ValueError('prompt+output cap exceeded')
        check={'coordinate_id':row['id'],'context_index':row['context_index'],'arm':row['arm'],'seed':row['seed'],
            'order':list(order),'ordered_schema_sha256':schema_sha,'ordered_request_sha256':s.ordered_digest(body),
            'typed_prompt_ids_sha256':s.ordered_digest(token_ids),'prompt_tokens':len(token_ids),
            'synthetic_output_tokens':len(tokenizer.encode(s.serialize(sample),add_special_tokens=False)),
            'expected_order_accepted_complete':True,'opposite_order_rejected':True}
        previous=old[row['context_index'],row['arm'],row['seed'],order]
        for key in ['ordered_schema_sha256','ordered_request_sha256','typed_prompt_ids_sha256','prompt_tokens','synthetic_output_tokens']:
            if check[key]!=previous[key]: raise ValueError('approved feasibility changed: '+key)
        checks.append(check);ids[row['id']]=token_ids
        prompts[row['id']]={'tokens':len(token_ids),'typed_token_ids_sha256':s.digest(token_ids),
            'physical_source':'vLLM typed tool.model_dump then pinned native HF template'}
        paired[row['context_index'],row['arm'],row['seed']].append(row)
    for rows in paired.values():
        if len(rows)!=2: raise ValueError('missing field-order mate')
        a,b=rows;x,y=requests[a['id']],requests[b['id']]
        if ids[a['id']]!=ids[b['id']]: raise ValueError('field-order prompt IDs differ')
        if s.serialize({k:v for k,v in x.items() if k!='structured_outputs'})!=s.serialize({k:v for k,v in y.items() if k!='structured_outputs'}):
            raise ValueError('more than grammar changed')
        if s.ordered_digest(x['structured_outputs'])==s.ordered_digest(y['structured_outputs']): raise ValueError('ordered grammars collapsed')
    if len(checks)!=48 or len(paired)!=24: raise ValueError('wrong study size')
    return {'requests':48,'order_only_physical_prompt_pairs':24,'schemas_compiled':len(schemas),'checks':checks,
        'rendered_prompts':prompts,'max_prompt_tokens':max(len(v) for v in ids.values()),
        'maximum_prompt_plus_output':max(len(v) for v in ids.values())+3072,
        'feasibility_crosswalk_sha256':s.file_hash(s.FEASIBILITY),'full_request_matches':48,
        'versions':{name:importlib.metadata.version(name) for name in ['vllm','xgrammar','transformers','tokenizers','httpx']},
        'gpu_calls':0,'model_calls':0,'fixture_labels':'First allowed enum for grammar only; not gold or model output'},ids


def seed_audit():
    paths=set()
    for sidecar in s.SIDE.iterdir():
        if not sidecar.is_dir() or sidecar==ROOT: continue
        for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
            paths.update(sidecar.glob(pattern))
    paths=sorted(p for p in paths if p.is_file())
    pattern=r'\b('+'|'.join(map(str,[s.MASTER,*s.SEEDS]))+r')\b'
    result=subprocess.run(['rg','-n',pattern,*map(str,paths)],capture_output=True,text=True,timeout=60)
    if result.returncode!=1 or result.stdout: raise ValueError('seed collision/audit failure: '+result.stdout[:1000])
    return {'master':s.MASTER,'sampling_seeds':s.SEEDS,'source_sha256':{str(p):s.file_hash(p) for p in paths},
        'exit_code':result.returncode,'matches':result.stdout,
        'scope':'Named top-level SPEC/READY/RECIPE/CAMPAIGN/SEED and one-level inputs PLAN; own namespace excluded, not global'}


def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']: raise ValueError('spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    if s.read(ROOT/'DATA.json')!=s.build_data(): raise ValueError('selected source contexts changed')
    expected=s.build_design(s.read(ROOT/'DATA.json'))
    expected['rendered_prompts']=s.read(ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected!=spec['design'] or len(expected['plan'])!=48: raise ValueError('frozen design changed')
    for row in expected['plan']:
        body=s.make_request(expected,row);key=row['id']
        if (s.serialize(body)!=s.serialize(spec['requests'][key]) or s.digest(body)!=spec['request_sha256'][key]
            or s.ordered_digest(body)!=spec['ordered_request_sha256'][key]
            or s.ordered_digest(body['structured_outputs']['json'])!=spec['ordered_schema_sha256'][key]):
            raise ValueError('ordered body/schema changed')


def prepare():
    if (ROOT/'SPEC.json').exists(): raise ValueError('already frozen')
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='': raise ValueError('CPU prepare requires CUDA hidden')
    data=s.build_data();design=s.build_design(data);audit=seed_audit()
    requests={r['id']:s.make_request(design,r) for r in design['plan']}
    qualification,ids=qualify(design,requests);design['rendered_prompts']=qualification['rendered_prompts']
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_study.py','test_driver.py'],
        cwd=ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    if tests.returncode: raise ValueError(tests.stdout[-4000:]+tests.stderr[-1000:])
    weight=weights()
    import owned
    values={'DATA.json':data,'CPU_QUALIFICATION.json':qualification,'PROMPT_IDS.json':ids,'WEIGHTS.json':weight,
        'SEED_AUDIT.json':audit,'DISPATCH.json':design['plan'],
        'SCHEMAS.json':{s.ordered_digest(b['structured_outputs']['json']):b['structured_outputs']['json'] for b in requests.values()},
        'CPU_TESTS.json':{'exit_code':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,
            'red':'Six desired study/owned tests failed before implementation; three driver tests failed before implementation',
            'fake_http_calls':7,'gpu_calls':0,'model_calls':0},
        'SOURCE_ADAPTERS.json':{'run_source_path':str(RUN_SOURCE),'run_source_sha256':RUN_SOURCE_SHA,'run_edits':RUN_EDITS,
            'run_adapted_sha256':RUN_ADAPTED_SHA256,'owned_edits':owned.EDITS,'owned_adapted_sha256':owned.ADAPTED_SHA256}}
    for name,value in values.items(): s.write_once(ROOT/name,value)
    sources=dict(s.PRIOR['source_sha256']);sources.update({str(p):h for p,h in s.PINS.items()})
    sources.update(s.read(s.FEASIBILITY)['source_sha256']);sources.update(weight['source_sha256'])
    sources.update({str(p):h for p,h in owned.PINNED.items()})
    sources[str(owned.SOURCE_PATH)]=owned.SOURCE_SHA256;sources[str(owned.OBSERVER_PATH)]=owned.OBSERVER_SHA
    sources.update({str(p):s.file_hash(p) for p in [*ROOT.glob('*.py'),*ROOT.glob('*.md'),*ROOT.glob('*.json')]})
    spec={'schema':ROOT.name,'design':design,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
        'ordered_request_sha256':{k:s.ordered_digest(v) for k,v in requests.items()},
        'ordered_schema_sha256':{k:s.ordered_digest(v['structured_outputs']['json']) for k,v in requests.items()},
        'source_sha256':sources,'weight':weight,'budget':{'calls':48,'workers':4,'collection_seconds':600,
            'work_seconds':780,'owned_seconds':900,'cleanup_seconds':120,'outer_seconds':930,'request_timeout_seconds':120,'max_tokens':3072,'retries':0},
        'frozen_before_model_calls':True,'alignment':'Assigned raw key order followed by unchanged displayed-record gold; no repair',
        'primary':'Meaningful-minus-ordinal within field order and their difference, tasks/context clusters separate'}
    spec['spec_id']=s.digest(spec);s.write_once(ROOT/'SPEC.json',spec)
    verify(spec);owned.load_suite()
    argv=[owned.PYTHON,str(ROOT/'owned.py'),'--directory',str(ROOT/'owned/attempt-001')]
    s.write_once(ROOT/'READY.json',{'status':'CPU_READY_PARENT_ACCEPTANCE_REQUIRED','calls':48,'spec_id':spec['spec_id'],
        'spec_sha256':s.file_hash(ROOT/'SPEC.json'),'source_sha256':{**sources,str(ROOT/'SPEC.json'):s.file_hash(ROOT/'SPEC.json')},
        'launch_argv':argv,'verify_argv':[owned.PYTHON,str(ROOT/'owned.py'),'--verify'],'cwd':str(ROOT),
        'budget':spec['budget'],'schemas_compiled':qualification['schemas_compiled'],'physical_prompt_pairs':24,
        'max_input_plus_output':qualification['maximum_prompt_plus_output'],'tests_exit0':True,'gpu_calls':0,'model_calls':0,
        'source_review_report':str(ROOT/'SOURCE_REVIEW.md'),'environment':'Parent actual MIG UUID/LD/key inherited; no CUDA0 hardcoding'})
    print(s.serialize({'ready_sha256':s.file_hash(ROOT/'READY.json'),'calls':48,'maximum_prompt_plus_output':qualification['maximum_prompt_plus_output']}),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','verify','run'])
    parser.add_argument('--endpoint',type=Path);parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch',type=float);args=parser.parse_args()
    if args.command=='prepare': prepare()
    elif args.command=='verify': verify(s.read(ROOT/'SPEC.json'));print('verified',flush=True)
    else:
        if not args.endpoint: parser.error('actual endpoint required')
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(),args.output_dir.resolve(),args.overall_start_epoch)))


if __name__=='__main__': main()
