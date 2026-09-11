"""Exact72 frozen component requests with qualified native wire and single-LoRA run seam."""
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

ROOT=s.ROOT;RUN_SOURCE=s.SIDE/'leaf-identity-counter-v1/driver.py'
RUN_SOURCE_SHA='f3c7bf409323d1854abfdb30efb64ead13c7a9de0dd6aadb5c64c7083e645580'
HTTP_SOURCE=s.padding.GRAMMAR/'driver.py'
if s.file_hash(RUN_SOURCE)!=RUN_SOURCE_SHA or s.file_hash(HTTP_SOURCE)!=s.padding.PINS[HTTP_SOURCE]:raise ValueError('qualified source changed')
loader=importlib.util.spec_from_file_location('shifted_private_native_http',HTTP_SOURCE)
qualified_http=importlib.util.module_from_spec(loader);loader.loader.exec_module(qualified_http);BASE=qualified_http.BASE
tree=ast.parse(RUN_SOURCE.read_text());node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
source=ast.get_source_segment(RUN_SOURCE.read_text(),node)
RUN_EDITS=[('96','72',3),('1080','750',2),('launch + 1200','launch + 870',1)]
for before,after,count in RUN_EDITS:
    if source.count(before)!=count:raise ValueError('run cardinality/cap seam changed: '+before)
    source=source.replace(before,after)
RUN_ADAPTED_SHA=hashlib.sha256(source.encode()).hexdigest()
exec(compile(source,str(RUN_SOURCE)+':shifted72-private','exec'),globals())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='weights')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(RUN_SOURCE)+':weights','exec'),globals())

def wire_hook(spec,output):
    by={h:key for key,h in spec['ordered_request_sha256'].items()}
    if len(by)!=len(spec['requests']):raise ValueError('ordered request collision')
    async def capture(request):
        if request.method!='POST' or not request.url.path.endswith('/chat/completions'):return
        h=hashlib.sha256(request.content).hexdigest();key=by.get(h)
        if key is None or request.content!=s.serialize(spec['requests'][key]).encode():raise ValueError('physical ordered request mismatch')
        s.write_once(output/'wire'/(key+'.json'),{'coordinate_id':key,'body_utf8':request.content.decode(),
            'body_sha256':h,'captured_epoch':time.time(),'credentials_recorded':False})
    return capture

def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']:raise ValueError('spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    data=s.read(ROOT/'DATA.json')
    if data!=s.build_data():raise ValueError('exposed context selection changed')
    expected=s.build_design(data);expected['rendered_prompts']=s.read(ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected!=spec['design'] or len(expected['plan'])!=72:raise ValueError('exact72 plan changed')
    for row in expected['plan']:
        body=s.make_request(expected,row);key=row['id']
        if s.serialize(body)!=s.serialize(spec['requests'][key]) or s.ordered_digest(body)!=spec['ordered_request_sha256'][key]:raise ValueError('request/schema order changed')

def qualify(design,requests):
    import xgrammar as xgr
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(BASE['path'],local_files_only=True,trust_remote_code=False)
    config=s.read(Path(BASE['path'])/'config.json')
    compiler=xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(tokenizer,vocab_size=config['vocab_size']),max_threads=2,cache_enabled=True)
    compiled={};checks=[];ids={};rendered={};negative=0
    for row in design['plan']:
        body=requests[row['id']];schema=body['structured_outputs']['json'];h=s.ordered_digest(schema)
        if h not in compiled:
            grammar=compiler.compile_json_schema(s.serialize(schema),any_whitespace=True);compiled[h]=grammar
            valid=[{'tag':item['properties']['tag']['const'],'label':item['properties']['label']['enum'][0]} for item in schema['prefixItems']]
            matcher=xgr.GrammarMatcher(grammar)
            if not matcher.accept_string(s.serialize(valid).encode()) or not matcher.is_completed():raise ValueError('exact valid grammar rejected')
            wrongtag=deepcopy(valid);wrongtag[-1]['tag']='q0000'
            wronglabel=deepcopy(valid);wronglabel[0]['label']='NOT_A_CANONICAL_LABEL'
            opposite=[{'label':v['label'],'tag':v['tag']} for v in valid]
            for bad in (wrongtag,wronglabel,opposite,valid[:-1]):
                matcher=xgr.GrammarMatcher(grammar)
                if matcher.accept_string(s.serialize(bad).encode()) and matcher.is_completed():raise ValueError('invalid grammar accepted')
                negative+=1
        prompt=qualified_http.typed_prompt_ids(tokenizer,body)
        if not prompt or len(prompt)+3072>8192:raise ValueError('full prompt/output exceeds8192')
        ids[row['id']]=prompt;rendered[row['id']]={'tokens':len(prompt),'typed_token_ids_sha256':s.digest(prompt)}
        sample=[{'tag':p['properties']['tag']['const'],'label':p['properties']['label']['enum'][0]} for p in schema['prefixItems']]
        checks.append({'coordinate_id':row['id'],'prompt_tokens':len(prompt),'ordered_schema_sha256':h,
            'synthetic_first_enum_output_tokens':len(tokenizer.encode(s.serialize(sample),add_special_tokens=False)),
            'typed_prompt_ids_sha256':s.digest(prompt),'fixture_not_sampled':True})
    for index in range(0,72,3):
        block=design['plan'][index:index+3]
        if len({s.digest(ids[r['id']]) for r in block})!=1:raise ValueError('cue conditions changed physical prompt IDs')
        bodies=[requests[r['id']] for r in block]
        if len({s.serialize({k:v for k,v in body.items() if k!='structured_outputs'}) for body in bodies})!=1:raise ValueError('more than schema changed')
    return {'requests':72,'same_physical_prompt_triples':24,'schemas_compiled':len(compiled),'negative_cases':negative,
        'rendered_prompts':rendered,'checks':checks,'max_input_plus_output':max(len(v) for v in ids.values())+3072,
        'versions':{k:importlib.metadata.version(k) for k in ('vllm','xgrammar','transformers','tokenizers','httpx')},
        'gpu_calls':0,'model_calls':0,'no_equal_realized_output_token_claim':True},ids

def seed_audit():
    paths=set()
    for directory in s.SIDE.iterdir():
        if not directory.is_dir() or directory==ROOT:continue
        for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
            paths.update(p for p in directory.glob(pattern) if p.is_file())
    paths=sorted(paths);pattern=r'\b('+'|'.join(map(str,[s.MASTER,*s.SEEDS]))+r')\b'
    result=subprocess.run(['rg','-n',pattern,*map(str,paths)],capture_output=True,text=True,timeout=60)
    if result.returncode!=1 or result.stdout:raise ValueError('seed collision/audit failure: '+result.stdout[:1000])
    return {'master':s.MASTER,'seeds':s.SEEDS,'exit_code':result.returncode,'matches':result.stdout,
        'source_sha256':{str(p):s.file_hash(p) for p in paths},
        'scope':'Existing sidecar top-level SPEC/READY/RECIPE/CAMPAIGN/SEED and inputs PLAN; own namespace excluded, not global'}

def prepare():
    if (ROOT/'SPEC.json').exists():raise ValueError('already frozen')
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU preparation requires CUDA hidden')
    data=s.build_data();design=s.build_design(data);requests={r['id']:s.make_request(design,r) for r in design['plan']}
    seeds=seed_audit();qualification,ids=qualify(design,requests);design['rendered_prompts']=qualification['rendered_prompts']
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_study.py','test_driver.py'],cwd=ROOT,
        capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    if tests.returncode:raise ValueError(tests.stdout[-4000:]+tests.stderr[-1000:])
    weight=weights();import owned
    values={'DATA.json':data,'REQUESTS.json':requests,'DISPATCH.json':design['plan'],'PROMPT_IDS.json':ids,
        'CPU_QUALIFICATION.json':qualification,'SEED_AUDIT.json':seeds,'WEIGHTS.json':weight,
        'CPU_TESTS.json':{'returncode':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,
            'red':'4 study/owned tests and3 driver tests failed before implementations existed','fake_http_calls':72,'gpu_calls':0},
        'SOURCE_ADAPTERS.json':{'run_source':str(RUN_SOURCE),'run_source_sha256':RUN_SOURCE_SHA,'run_edits':RUN_EDITS,
            'run_adapted_sha256':RUN_ADAPTED_SHA,'owned_edits':owned.EDITS,'owned_adapted_sha256':owned.ADAPTED_SHA256,
            'unchanged_real_launcher':str(s.SIDE/'leaf-role-routing-v1/source/serve.py')}}
    for name,value in values.items():s.write_once(ROOT/name,value)
    sources=dict(s.read(s.PARENT/'SPEC.json')['source_sha256']);sources.update({str(p):h for p,h in s.PINS.items()})
    sources.update(weight['source_sha256']);sources.update({str(p):h for p,h in owned.PINNED.items()})
    sources.update({str(RUN_SOURCE):RUN_SOURCE_SHA,str(HTTP_SOURCE):s.padding.PINS[HTTP_SOURCE],
                    str(owned.SOURCE_PATH):owned.SOURCE_SHA256,str(owned.OBSERVER_PATH):owned.OBSERVER_SHA})
    sources.update({str(p):s.file_hash(p) for p in [*ROOT.glob('*.py'),*ROOT.glob('*.md'),*ROOT.glob('*.json')]})
    budget={'calls':72,'workers':4,'collection_seconds':600,'work_seconds':750,'owned_seconds':870,
            'outer_seconds':900,'cleanup_seconds':120,'request_timeout_seconds':120,'output_cap':3072,'retries':0}
    spec={'schema':ROOT.name,'design':design,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
        'ordered_request_sha256':{k:s.ordered_digest(v) for k,v in requests.items()},'source_sha256':sources,'weight':weight,
        'budget':budget,'frozen_before_model_calls':True,'named_alignment':'Secondary only, shifted index(i+17)%64, never primary repair'}
    spec['spec_id']=s.digest(spec);s.write_once(ROOT/'SPEC.json',spec);verify(spec);owned.load_suite()
    s.write_once(ROOT/'READY.json',{'status':'CPU_READY_PARENT_ACCEPTANCE_REQUIRED','spec_sha256':s.file_hash(ROOT/'SPEC.json'),
        'source_sha256':{**sources,str(ROOT/'SPEC.json'):s.file_hash(ROOT/'SPEC.json')},'budget':budget,
        'launch_argv':[owned.PYTHON,str(ROOT/'owned.py'),'--directory',str(ROOT/'owned/attempt-001')],
        'verify_argv':[owned.PYTHON,str(ROOT/'owned.py'),'--verify'],'cwd':str(ROOT),'output':str(ROOT/'outputs/attempt-001'),
        'max_input_plus_output':qualification['max_input_plus_output'],'prompt_triples':24,'gpu_calls':0,'model_calls':0})
    print(s.serialize({'ready_sha256':s.file_hash(ROOT/'READY.json'),'calls':72,'max_input_plus_output':qualification['max_input_plus_output']}),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('prepare','verify','run'))
    parser.add_argument('--endpoint',type=Path);parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch',type=float);args=parser.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='verify':verify(s.read(ROOT/'SPEC.json'));print('verified; no model calls')
    else:
        if not args.endpoint:parser.error('actual endpoint required')
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(),args.output_dir.resolve(),args.overall_start_epoch)))
if __name__=='__main__':main()
