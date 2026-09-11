"""CPU-only native rendering, focused qualification and immutable READY seal."""
import argparse,copy,hashlib,importlib.metadata,os,subprocess,time
from pathlib import Path
import protocol as p
import study as s

def typed_ids(tok,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    parsed=ChatCompletionRequest.model_validate(copy.deepcopy(body))
    if parsed.tools or parsed.tool_choice not in (None,'none'):raise ValueError('tools advertised')
    return tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**parsed.chat_template_kwargs)
def inputs():
    import xgrammar as xg
    started=time.time();contexts=p.contexts();plan=p.plan();tok=s.tokenizer();requests={r['id']:p.request(contexts[r['context_index']],r) for r in plan}
    prompts={k:typed_ids(tok,v) for k,v in requests.items()};maximum=max(map(len,prompts.values()))+3072
    if maximum>8192:raise ValueError('context cap exceeded')
    for block in range(16):
        rows=[r for r in plan if r['block']==block];a,b=(requests[r['id']] for r in rows)
        if {k:v for k,v in a.items() if k not in ('messages','structured_outputs')}!={k:v for k,v in b.items() if k not in ('messages','structured_outputs')}:raise ValueError('paired envelope differs')
        if a['messages'][0]!=b['messages'][0]:raise ValueError('paired system differs')
        sa,sb=(copy.deepcopy(v['structured_outputs']) for v in (a,b))
        taga=[i['properties']['tag'].pop('const') for i in sa['json']['prefixItems']]
        tagb=[i['properties']['tag'].pop('const') for i in sb['json']['prefixItems']]
        if sa!=sb or sorted(taga)!=sorted(tagb):raise ValueError('schema shape/tag multiset differs')
    config=s.read(Path(s.MODEL['path'])/'config.json');vocab=config.get('text_config',config)['vocab_size']
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocab),max_threads=2,cache_enabled=True)
    grammar_checks=[]
    for context in contexts:
        for arm in p.ARMS:
            compiled=compiler.compile_json_schema(s.serialize(p.schema(context,arm)['json']),any_whitespace=True)
            def accepts(value):
                matcher=xg.GrammarMatcher(compiled)
                return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
            tags=p.expected_tags(context,arm)
            # Three homogeneous arrays cover every label at every position, without gold.
            for label in p.LABELS:
                assert accepts([dict(tag=tag,label=label) for tag in tags])
            legal=[dict(tag=tag,label=p.LABELS[i%3]) for i,tag in enumerate(tags)]
            assert accepts(legal)
            invalid=[]
            bad=copy.deepcopy(legal);bad[0]['tag']=tags[1];invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0],bad[1]=bad[1],bad[0];invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0]['label']='unknown';invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0]['extra']='x';invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0]={'label':bad[0]['label'],'tag':bad[0]['tag']};invalid.append(bad)
            invalid.extend([legal[:-1],legal+[legal[-1]]])
            assert all(not accepts(value) for value in invalid)
            mutated=copy.deepcopy(context)
            for record in mutated['records']:record['gold_label']='DO_NOT_LEAK_GOLD'
            assert p.schema(mutated,arm)==p.schema(context,arm)
            grammar_checks.append(dict(arm=arm,schema_sha256=s.digest(p.schema(context,arm)),positions=48,
                all_three_labels_at_every_position=True,valid_vectors=4,invalid_vectors=len(invalid),
                gold_mutation_invariant=True))
    ancestor=s.read(s.SOURCE/'PLAN.json');ancestor_requests=s.read(s.SOURCE/'REQUESTS.json')
    ancestor_prefix=s.read(s.SOURCE/'PROMPT_IDS.json')
    for row in plan:
        old=next(r for r in ancestor if r['context_index']==row['context_index'] and r['arm']==row['arm'])
        assert requests[row['id']]['messages']==ancestor_requests[old['id']]['messages']
        assert prompts[row['id']]==ancestor_prefix[old['id']]
    paths=[]
    for directory in s.SIDE.iterdir():
        if directory.is_dir() and directory!=s.ROOT:paths.extend(f for f in directory.iterdir() if f.is_file() and f.suffix in ('.json','.py','.yaml'))
    scan=subprocess.run(['rg','-n',r'\b981581[0-9]{3}\b',*map(str,paths)],capture_output=True,text=True,timeout=60)
    if scan.returncode!=1:raise ValueError('seed collision/scan failure: '+scan.stdout[:1000]+scan.stderr[:300])
    values={'PLAN.json':plan,'REQUESTS.json':requests,'PROMPT_IDS.json':prompts,
        'ORDERED_REQUESTS.json':{k:s.serialize(v) for k,v in requests.items()},
        'SEED_AUDIT.json':dict(master=p.MASTER,seeds=sorted({r['seed'] for r in plan}),scanned_paths=len(paths),returncode=scan.returncode),
        'CPU_NATIVE.json':dict(passed=True,requests=32,max_input_plus_output=maximum,output_allowance=3072,context_cap=8192,
            exact_grammar_checks=grammar_checks,pair_envelopes_equal_except_public_tag_consts=True,ancestor_messages_and_native_prefixes_identical=True,tools_advertised=0,gpu_calls=0,model_service_calls=0,
            versions={n:importlib.metadata.version(n) for n in ('vllm','transformers','xgrammar','httpx')},
            request_wire_sha256={k:hashlib.sha256(s.serialize(v).encode()).hexdigest() for k,v in requests.items()},elapsed_seconds=time.time()-started)}
    for name,value in values.items():s.write(s.ROOT/name,value)
    print(dict(requests=32,max_input_plus_output=maximum))
def qualify():
    command=[str(s.NATIVE),'-m','unittest','-v','test_science','test_owner','test_collect'];started=time.time()
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    receipt=dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,passed=result.returncode==0,
        elapsed_seconds=time.time()-started,gpu_calls=0,model_service_calls=0,source_sha256={str(path):s.sha(path) for path in s.ROOT.glob('*.py')})
    s.write(s.ROOT/'CPU_TESTS_V2.json',receipt)
    if result.returncode:raise ValueError('focused tests failed')
    print(result.stderr)
def seal():
    import owner
    tests=s.read(s.ROOT/'CPU_TESTS_V2.json');native=s.read(s.ROOT/'CPU_NATIVE.json')
    if not tests['passed'] or not native['passed']:raise ValueError('fresh CPU proof required')
    for path,pin in tests['source_sha256'].items():
        if s.sha(path)!=pin:raise ValueError('test source changed')
    inherited=s.read(s.SOURCE/'READY_V2.json');source=dict(inherited['source_sha256']);source[str(s.SOURCE/'READY_V2.json')]=s.sha(s.SOURCE/'READY_V2.json')
    for path in s.ROOT.iterdir():
        if path.is_file() and path!=s.READY_PATH:source[str(path)]=s.sha(path)
    for path,pin in source.items():
        if s.sha(path)!=pin:raise ValueError('source closure changed: '+path)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,model=s.MODEL,adapter=None,planned_endpoints=32,
        contexts=8,pairs_per_context=48,research_exposed_panel=True,decoder='exact_public_requested_tag_both_arms',labels_unconstrained_by_gold=True,work_seconds=1080,owned_seconds=1170,outer_seconds=1200,
        cleanup_seconds=90,outer_margin_seconds=30,startup_seconds=180,workers=4,request_seconds=90,seed_master=p.MASTER,
        provider_billing='unknown/not measured',actual_service_wrapper=str(s.ROOT/'service_wrapper.py'),
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],gpu_calls=0,model_service_calls=0,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(dict(sha256=s.sha(s.READY_PATH),identity=ready['identity'],pins=len(source)))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));a=ap.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU preparation requires hidden GPUs')
    globals()[a.command]()
