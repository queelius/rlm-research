"""Bounded CPU preparation; no service, GPU allocation or scientific inference."""
import argparse
import copy
import hashlib
import importlib.metadata
import os
from pathlib import Path
import subprocess
import time
import protocol as p
import study as s


def typed_ids(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    parsed=ChatCompletionRequest.model_validate(copy.deepcopy(body))
    if parsed.tools or parsed.tool_choice not in (None,'none'):
        raise ValueError('final-only request advertised tools')
    return tokenizer.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,
        tokenize=True,return_dict=False,**parsed.chat_template_kwargs)


def inputs():
    import xgrammar as xg
    started=time.time();data=s.read(s.ROOT/'DATA.json');plan=s.read(s.ROOT/'PLAN.json');tok=s.tokenizer()
    requests={r['id']:p.request(p.selected_context(data['contexts'][r['context_index']],r),r,data['constant']) for r in plan}
    prompts={key:typed_ids(tok,body) for key,body in requests.items()}
    maximum=max(map(len,prompts.values()))+3072
    if maximum>8192:raise ValueError(f'Full selected source exceeds native context budget: {maximum}; no cropping/substitution permitted')
    for row in plan:
        body=requests[row['id']];ctx=p.selected_context(data['contexts'][row['context_index']],row)
        mutation=copy.deepcopy(ctx)
        for record in mutation['records']:
            record['gold_label']='mutated';record['original_pairID']='leaky';record['original_promptID']='leaky'
        if p.request(mutation,row,data['constant'])!=body:raise ValueError('host metadata leaked')
        if not tok.decode(prompts[row['id']][-16:]).endswith('<|im_start|>assistant\n'):raise ValueError('native assistant prefix differs')
        if row['decoder']=='shape':
            other=next(r for r in plan if r['kind']==row['kind'] and r['block']==row['block'] and r['arm']==row['arm'] and r['decoder']=='free')
            if {k:v for k,v in body.items() if k!='structured_outputs'}!=requests[other['id']] or prompts[row['id']]!=prompts[other['id']]:
                raise ValueError('free/shape scientific pairing differs')
    config=s.read(Path(s.MODEL['path'])/'config.json');vocab=config.get('text_config',config)['vocab_size']
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocab),max_threads=2,cache_enabled=True)
    compiled=compiler.compile_json_schema(s.serialize(p.schema(48)['json']),any_whitespace=True)
    positives=[];negatives=[]
    for tag in (data['constant'],'mffffffffffff',data['contexts'][0]['records'][-1]['id']):
        for label in p.LABELS:positives.append([dict(tag=tag,label=label) for _ in range(48)])
    legal=positives[0]
    negatives.extend([legal[:-1],legal+[legal[-1]]])
    for key,value in (('label','unknown'),('tag','mBAD')):
        bad=copy.deepcopy(legal);bad[0][key]=value;negatives.append(bad)
    for expected,values in ((True,positives),(False,negatives)):
        for value in values:
            matcher=xg.GrammarMatcher(compiled)
            accepted=matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
            if accepted!=expected:raise ValueError('generic grammar fixture mismatch')
    paths=[]
    for directory in s.SIDE.iterdir():
        if directory.is_dir() and directory!=s.ROOT:
            paths.extend(f for f in directory.iterdir() if f.is_file() and f.suffix in ('.json','.py','.yaml'))
    scan=subprocess.run(['rg','-n',r'\b981431[0-9]{3}\b',*map(str,paths)],capture_output=True,text=True,timeout=60)
    if scan.returncode!=1:raise ValueError('seed collision/scan failure: '+scan.stdout[:1000]+scan.stderr[:500])
    values={'REQUESTS_V2.json':requests,'PROMPT_IDS_V2.json':prompts,
        'ORDERED_REQUESTS_V2.json':{key:s.serialize(body) for key,body in requests.items()},
        'SEED_AUDIT_V2.json':dict(master=p.MASTER,seeds=sorted({r['seed'] for r in plan}),scanned_paths=len(paths),
            scope='Sibling top-level JSON/Python/YAML, own namespace excluded',returncode=scan.returncode),
        'CPU_NATIVE_V2.json':dict(passed=True,requests=80,primary=64,singletons=16,
            input_tokens={key:len(value) for key,value in prompts.items()},max_input_plus_output=maximum,
            output_allowance=3072,context_cap=8192,generic_grammar_positive_cases=len(positives),
            generic_grammar_negative_cases=len(negatives),free_shape_native_prefix_equal=True,
            host_gold_and_original_ids_mutation_invariant=True,tools_advertised=0,gpu_calls=0,model_service_calls=0,
            versions={name:importlib.metadata.version(name) for name in ('vllm','transformers','xgrammar','httpx')},
            request_wire_sha256={key:hashlib.sha256(s.serialize(body).encode()).hexdigest() for key,body in requests.items()},
            qualified_source_sha256={str(s.ROOT/name):s.sha(s.ROOT/name) for name in ('protocol.py','prepare.py','study.py')},
            elapsed_seconds=time.time()-started)}
    for name,value in values.items():s.write(s.ROOT/name,value)
    print(dict(requests=80,max_input_plus_output=maximum,grammar_positive=len(positives),grammar_negative=len(negatives)))


def qualify():
    command=[str(s.NATIVE),'-m','unittest','-v','test_science','test_owner','test_collect']
    started=time.time();result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True,timeout=120,
        env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    receipt=dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        passed=result.returncode==0,elapsed_seconds=time.time()-started,gpu_calls=0,model_service_calls=0,
        source_sha256={str(path):s.sha(path) for path in s.ROOT.glob('*.py')})
    s.write(s.ROOT/'CPU_TESTS.json',receipt)
    if result.returncode:raise ValueError('focused tests failed; result retained')
    print(result.stderr)


def seal():
    import owner
    for name,key in (('CPU_TESTS.json','source_sha256'),('CPU_NATIVE_V2.json','qualified_source_sha256')):
        proof=s.read(s.ROOT/name)
        if not proof['passed'] or any(s.sha(path)!=pin for path,pin in proof[key].items()):raise ValueError('fresh CPU proof required')
    inherited=s.SIDE/'root-record-interface-v1/READY.json';source=dict(s.read(inherited)['source_sha256'])
    source[str(inherited)]=s.sha(inherited)
    native=s.SIDE/'leaf-role-tool-contract-v1/scoring_v2.py';source[str(native)]=s.sha(native)
    manifest=s.read(s.ROOT/'SOURCE_MANIFEST.json')
    # Preserve all acquisition files, not just the derived dataset.
    cache=Path('/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2')
    for path in cache.iterdir():
        if path.is_file():source[str(path)]=s.sha(path)
    for path in s.ROOT.iterdir():
        if path.is_file() and path!=s.READY_PATH:source[str(path)]=s.sha(path)
    for path,pin in source.items():
        if s.sha(path)!=pin:raise ValueError('source closure changed: '+path)
    suite=owner.suite()
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,model=s.MODEL,adapter=None,
        primary_endpoints=64,singleton_endpoints=16,planned_endpoints=80,contexts=8,premises=128,pairs=384,
        work_seconds=2490,owned_seconds=2610,outer_seconds=2700,cleanup_seconds=120,outer_margin_seconds=90,
        startup_seconds=180,collection_reserve_seconds=60,workers=4,request_seconds=90,
        seed_master=p.MASTER,source_manifest=str(s.ROOT/'SOURCE_MANIFEST.json'),
        provider_billing='unknown/not measured',actual_service_wrapper=str(suite.SERVE),
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],
        gpu_calls=0,model_service_calls=0,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify()
    print(dict(sha256=s.sha(s.READY_PATH),identity=ready['identity'],pins=len(source)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('inputs','qualify','seal'))
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU preparation requires hidden GPUs')
    globals()[parser.parse_args().command]()
