"""Native CPU grammar/prompt qualification and parent-only bounded collection."""
import argparse
import ast
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
import httpx
import study as s

ROOT=s.ROOT
HTTP_SOURCE=s.padding.GRAMMAR/'driver.py'
if s.file_hash(HTTP_SOURCE)!=s.padding.PINS[HTTP_SOURCE]:raise ValueError('qualified HTTP helper changed')
loader=importlib.util.spec_from_file_location('reminder_native_http',HTTP_SOURCE);qualified_http=importlib.util.module_from_spec(loader);loader.loader.exec_module(qualified_http)
BASE=qualified_http.BASE;wire_hook=qualified_http.wire_hook
RUN_SOURCE=ROOT.parent/'leaf-identity-counter-v1/driver.py';RUN_SOURCE_SHA='f3c7bf409323d1854abfdb30efb64ead13c7a9de0dd6aadb5c64c7083e645580'
if s.file_hash(RUN_SOURCE)!=RUN_SOURCE_SHA:raise ValueError('qualified run changed')
raw=RUN_SOURCE.read_text();tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run');source=ast.get_source_segment(raw,node)
RUN_EDITS=[('launch + 1200','launch + 870',1),('launch + 1080','launch + 750',2)]
for before,after,count in RUN_EDITS:
    if source.count(before)!=count:raise ValueError('run cap seam changed')
    source=source.replace(before,after)
RUN_ADAPTED_SHA256=hashlib.sha256(source.encode()).hexdigest();exec(compile(source,str(RUN_SOURCE)+':phase192-private','exec'),globals())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='weights');exec(compile(ast.Module(body=[node],type_ignores=[]),str(RUN_SOURCE)+':weights','exec'),globals())

def seed_audit():
    paths=set()
    for child in s.SIDE.iterdir():
        if not child.is_dir() or child==ROOT:continue
        for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
            paths.update(p for p in child.glob(pattern) if p.is_file())
    pattern=r'\b('+'|'.join(map(str,[s.MASTER,*s.SEEDS]))+r')\b'
    result=subprocess.run(['rg','-n',pattern,*map(str,sorted(paths))],capture_output=True,text=True,timeout=60)
    if result.returncode!=1 or result.stdout:raise ValueError('seed collision/audit failure: '+result.stdout[:1000])
    return {'master':s.MASTER,'sampling_seeds':s.SEEDS,'source_sha256':{str(p):s.file_hash(p) for p in paths},'exit_code':1,'matches':'',
            'scope':'small named frozen manifests; own namespace excluded; not global','superseded_proposal':'981308 collided active SFT; MAIN assigned981310'}

def qualify(design,requests):
    import xgrammar as xgr
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(BASE['path'],local_files_only=True,trust_remote_code=False)
    config=s.read(Path(BASE['path'])/'config.json');compiler=xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(tokenizer,vocab_size=config['vocab_size']),max_threads=2,cache_enabled=True)
    ids={};prompts={};schemas={};checks=[];equal=[]
    for row in design['plan']:
        key=row['id'];body=requests[key];schema=body['structured_outputs']['json'];sha=s.ordered_digest(schema)
        gold=design['batches'][row['batch_id']]['gold'];sample=s.synthetic_output(gold,gold['labels'][0]);phase=row['phase'];nonanchor=(phase+1)%4
        if sha not in schemas:
            compiled=compiler.compile_json_schema(s.serialize(schema),any_whitespace=True);matcher=xgr.GrammarMatcher(compiled)
            if not matcher.accept_string(s.serialize(sample).encode()) or not matcher.is_completed():raise ValueError('phase fixture rejected')
            bads={}
            bad=deepcopy(sample);bad[phase]=dict(reversed(list(bad[phase].items())));bads['reversed_order']=s.serialize(bad)
            bad=deepcopy(sample);bad[nonanchor]={'label':gold['labels'][0]};bads['wrong_phase_object']=s.serialize(bad)
            bad=deepcopy(sample);bad[phase]=gold['labels'][0];bads['wrong_phase_string']=s.serialize(bad)
            bad=deepcopy(sample);bad[60+phase]['tag']='q999999';bads['late_wrong_tag']=s.serialize(bad)
            bad=deepcopy(sample);bad[phase]['extra']='x';bads['extra_key']=s.serialize(bad)
            bad=deepcopy(sample);del bad[phase]['label'];bads['missing_key']=s.serialize(bad)
            bad=deepcopy(sample);bad[nonanchor]='not_a_label';bads['noncanonical']=s.serialize(bad)
            bads.update(short=s.serialize(sample[:-1]),long=s.serialize(sample+[sample[-1]]),duplicate=s.serialize(sample).replace('"tag":','"tag":"duplicate","tag":',1))
            for name,text in bads.items():
                matcher=xgr.GrammarMatcher(compiled)
                if matcher.accept_string(text.encode()) and matcher.is_completed():raise ValueError('bad fixture accepted: '+name)
            schemas[sha]={'phase':phase,'accepted':True,'rejected_complete':list(bads)}
        token_ids=qualified_http.typed_prompt_ids(tokenizer,body)
        if not token_ids or len(token_ids)+3072>8192:raise ValueError('prompt plus complete allowance does not fit')
        ids[key]=token_ids;prompts[key]={'tokens':len(token_ids),'typed_token_ids_sha256':s.digest(token_ids)}
        checks.append({'id':key,'phase':phase,'ordered_schema_sha256':sha,'objects':16,'strings':48,'prompt_tokens':len(token_ids),
            'synthetic_output_tokens':{label:len(tokenizer.encode(s.serialize(s.synthetic_output(gold,label)),add_special_tokens=False)) for label in gold['labels']}})
    for group in s.dispatch_units(design):
        first=group[0];common={k:v for k,v in requests[first['id']].items() if k!='structured_outputs'}
        for row in group[1:]:
            if common!={k:v for k,v in requests[row['id']].items() if k!='structured_outputs'} or ids[first['id']]!=ids[row['id']]:raise ValueError('schema-only physical prompt invariance failed')
            equal.append([first['id'],row['id']])
    if len(ids)!=192 or len(equal)!=168 or len(schemas)!=60:raise ValueError('exact qualification coverage differs')
    return {'requests':192,'schemas_compiled':len(schemas),'schema_checks':schemas,'checks':checks,'all_condition_prompt_pairs':equal,
        'all_condition_prompt_equal_units':24,'rendered_prompts':prompts,'max_prompt_tokens':max(map(len,ids.values())),
        'maximum_prompt_plus_output':max(map(len,ids.values()))+3072,'versions':{n:importlib.metadata.version(n) for n in ('vllm','xgrammar','transformers','tokenizers','httpx')},
        'python':sys.version,'gpu_calls':0,'model_calls':0,'synthetic_caution':'Repeated labels prove structure only, not semantic outcomes or arbitrary output-token maximum'},ids

def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']:raise ValueError('spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    if s.read(ROOT/'DATA.json')!=s.build_data():raise ValueError('source data changed')
    design=s.build_design(s.read(ROOT/'DATA.json'));design['rendered_prompts']=s.read(ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if design!=spec['design'] or len(design['plan'])!=192:raise ValueError('fixed192 design changed')
    for row in design['plan']:
        body=s.make_request(design,row);key=row['id']
        if s.serialize(body)!=s.serialize(spec['requests'][key]) or s.digest(body)!=spec['request_sha256'][key] or s.ordered_digest(body)!=spec['ordered_request_sha256'][key]:raise ValueError('request/order changed')

def prepare():
    if (ROOT/'SPEC.json').exists() or (ROOT/'READY.json').exists():raise ValueError('already frozen')
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU qualification requires hidden CUDA')
    audit=seed_audit();data=s.build_data();design=s.build_design(data);requests={r['id']:s.make_request(design,r) for r in design['plan']}
    qualification,ids=qualify(design,requests);design['rendered_prompts']=qualification['rendered_prompts']
    print(s.serialize({'qualified':192,'schemas':qualification['schemas_compiled'],'max_prompt_plus_output':qualification['maximum_prompt_plus_output']}),flush=True)
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_study.py','test_driver.py'],cwd=ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    if tests.returncode:raise ValueError(tests.stdout[-4000:]+tests.stderr[-1000:])
    import owned
    weight=weights();values={'DATA.json':data,'DISPATCH.json':design['plan'],'REQUESTS.json':requests,'PROMPT_IDS.json':ids,
        'CPU_QUALIFICATION.json':qualification,'WEIGHTS.json':weight,'SEED_AUDIT.json':audit,'CPU_TESTS.json':{'returncode':0,'stdout':tests.stdout,'stderr':tests.stderr,'red':'12 tests failed missing modules before implementation','fake_http_only':True,'gpu_calls':0},
        'SOURCE_ADAPTERS.json':{'run_source_path':str(RUN_SOURCE),'run_source_sha256':RUN_SOURCE_SHA,'run_edits':RUN_EDITS,'run_adapted_sha256':RUN_ADAPTED_SHA256,
            'collector_source_path':str(s.COLLECTOR_PATH),'collector_source_sha256':s.COLLECTOR_SHA,'grouped_body_source':str(s.CUE/'study.py'),
            'grouped_body_source_sha256':s.PINS[s.CUE/'study.py'],'collector_adapted_sha256':s.COLLECT_ADAPTED_SHA,
            'delta':'Unchanged qualified sequential-unit collector body; dispatch_units validates8 rather than4. Original request/capture/finally/gather remain.',
            'owned_source_path':str(owned.SOURCE_PATH),'owned_source_sha256':owned.SOURCE_SHA256,'owned_edits':owned.EDITS,'owned_adapted_sha256':owned.ADAPTED_SHA256,
            'observer_path':str(owned.OBSERVER_PATH),'observer_sha256':owned.OBSERVER_SHA}}
    for name,value in values.items():s.write_once(ROOT/name,value)
    sources=dict(s.read(s.PARENT/'SPEC.json')['source_sha256']);sources.update({str(p):h for p,h in {**s.cue.PINS,**s.PINS}.items()});sources.update(weight['source_sha256'])
    sources.update({str(p):h for p,h in owned.PINNED.items()});sources.update({str(owned.SOURCE_PATH):owned.SOURCE_SHA256,str(owned.OBSERVER_PATH):owned.OBSERVER_SHA,str(RUN_SOURCE):RUN_SOURCE_SHA})
    sources.update({str(p):s.file_hash(p) for p in [*ROOT.glob('*.py'),*ROOT.glob('*.md'),*ROOT.glob('*.json')]})
    budget={'calls':192,'collection_seconds':600,'work_seconds':750,'owned_seconds':870,'cleanup_seconds':120,'parent_seconds':900,'concurrent_units':4,'unit_calls':8,'workers':4,'request_timeout_seconds':120,'max_tokens':3072,'retries':0}
    spec={'schema':ROOT.name,'design':design,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},'ordered_request_sha256':{k:s.ordered_digest(v) for k,v in requests.items()},
        'source_sha256':sources,'weight':weight,'budget':budget,'frozen_before_model_calls':True,
        'primary':'Same61 records: [(M-C)d0-(M-C)d3]; complete8call blocks,2seeds/context,4equalcontexts/task',
        'analysis_status':'Implementer projection, independent audit required'}
    spec['spec_id']=s.digest(spec);s.write_once(ROOT/'SPEC.json',spec);verify(spec);owned.load_suite()
    s.write_once(ROOT/'READY.json',{'status':'CPU_READY_PARENT_ACCEPTANCE_REQUIRED','calls':192,'spec_sha256':s.file_hash(ROOT/'SPEC.json'),'spec_id':spec['spec_id'],
        'source_sha256':{**sources,str(ROOT/'SPEC.json'):s.file_hash(ROOT/'SPEC.json')},'launch_argv':[owned.PYTHON,str(ROOT/'owned.py'),'--directory',str(ROOT/'owned/attempt-001')],
        'verify_argv':[owned.PYTHON,str(ROOT/'owned.py'),'--verify'],'cwd':str(ROOT),'budget':budget,'output':str(ROOT/'outputs/attempt-001'),
        'owned_directory':str(ROOT/'owned/attempt-001'),'max_input_plus_output':qualification['maximum_prompt_plus_output'],'schemas_compiled':60,
        'all_condition_prompt_equal_units':24,'tests_exit0':True,'gpu_calls':0,'model_calls':0,'authority':'MAIN alone accepts/launches; exact owned cleanup in finally'})
    print(s.serialize({'ready_sha256':s.file_hash(ROOT/'READY.json'),'calls':192}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','verify','run'));p.add_argument('--endpoint',type=Path)
    p.add_argument('--output-dir',type=Path,default=ROOT/'outputs/attempt-001');p.add_argument('--overall-start-epoch',type=float);a=p.parse_args()
    if a.command=='prepare':prepare()
    elif a.command=='verify':verify(s.read(ROOT/'SPEC.json'));print('verified')
    else:
        if not a.endpoint:p.error('authenticated endpoint required')
        raise SystemExit(asyncio.run(run(a.endpoint.resolve(),a.output_dir.resolve(),a.overall_start_epoch)))
if __name__=='__main__':main()
