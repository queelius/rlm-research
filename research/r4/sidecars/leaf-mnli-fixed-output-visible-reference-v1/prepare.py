"""CPU-only immutable preparation; never reads ancestor output directories."""
import copy,hashlib,importlib.metadata,json,os,subprocess,time
from collections import Counter
from pathlib import Path
import study as s,protocol as p
def typed(tok,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value=ChatCompletionRequest.model_validate(copy.deepcopy(body));assert not value.tools
    return tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**value.chat_template_kwargs)
def inputs():
    started=time.time();ancestor=s.read(s.ANCESTOR/'READY.json')
    if s.sha(s.ANCESTOR/'READY.json')!='dc9dd740a42f97d08e2ff89e96f2e0425e44e5e7546bde2f4635b72a989d4863':raise ValueError('ancestor READY changed')
    for name in ('DATA.json','PUBLIC.json'):
        path=s.ANCESTOR/name;assert s.sha(path)==ancestor['input_sha256'][str(path)]
        with (s.ROOT/name).open('xb') as f:f.write(path.read_bytes())
    cs=p.contexts();tok=s.tokenizer();aliases=p.unrelated_dictionary();rows=p.plan()
    named=[]
    for directory in sorted(s.SIDE.glob('*mnli*')):
        if directory==s.ROOT:continue
        for name in ('DATA.json','PUBLIC.json','PLAN.json','REQUESTS.json','READY.json','READY_v2.json','ALIEN_DICTIONARIES.json','UNRELATED_IDS.json'):
            path=directory/name
            if path.exists():named.append(path)
    manifest='\n'.join(path.read_text() for path in named)
    alias_set={v for values in aliases.values() for v in values};seeds=sorted({r['seed'] for r in rows})
    assert len(alias_set)==768 and not any(v in manifest for v in alias_set)
    assert not any(str(seed) in manifest for seed in seeds)
    requests={r['id']:p.request(cs[r['context_index']],r) for r in rows};ordered={k:s.serialize(v) for k,v in requests.items()};prompts={k:typed(tok,v) for k,v in requests.items()}
    checks=[]
    for ci,c in enumerate(cs):
        group=[r for r in rows if r['context_index']==ci];bs=[requests[r['id']] for r in group]
        original=s.read(s.ANCESTOR/'PLAN.json');prior=next(r for r in original if r['context_index']==ci and r['arm']=='shift17');priorbody=s.read(s.ANCESTOR/'REQUESTS.json')[prior['id']]
        assert all(b['structured_outputs']==priorbody['structured_outputs'] for b in bs)
        for b in bs:
            assert {k:v for k,v in b.items() if k not in ('messages','seed','cache_salt')}=={k:v for k,v in priorbody.items() if k not in ('messages','seed','cache_salt')}
            assert b['messages'][0]==priorbody['messages'][0]
            before=b['messages'][1]['content'].split('Input records (id, premise, hypothesis, requested_tag):\n')[0]
            assert before==priorbody['messages'][1]['content'].split('Input records (id, premise, hypothesis, requested_tag):\n')[0]
        lengths={r['arm']:len(prompts[r['id']]) for r in group};assert len(set(lengths.values()))==1
        assert all(len(tok.encode(x,add_special_tokens=False))==len(tok.encode(r['id'],add_special_tokens=False)) for x,r in zip(aliases[str(ci)],c['records']))
        changed=copy.deepcopy(c)
        for r in changed['records']:r['gold_label']='contradiction' if r['gold_label']!='contradiction' else 'neutral'
        for row in group:assert p.request(changed,row)==p.request(c,row)
        checks.append(dict(context=ci,genre=c['genre'],native_input_tokens=lengths,grammar_sha256=s.digest(bs[0]['structured_outputs']),gold_mutation_no_request_effect=True))
    import xgrammar as xg
    config=s.read(Path(s.MODEL['path'])/'config.json');config=config.get('text_config',config)
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=config['vocab_size']),max_threads=2,cache_enabled=True)
    for c in cs:
        grammar=compiler.compile_json_schema(s.serialize(p.schema(c,'wrong')['json']),any_whitespace=True)
        def accepts(value):
            matcher=xg.GrammarMatcher(grammar);return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
        tags=p.expected_tags(c,'wrong')
        for label in p.LABELS:assert accepts([dict(tag=t,label=label) for t in tags])
        bad=[dict(tag=t,label='neutral') for t in tags];bad[0]['tag']=tags[1];assert not accepts(bad)
    provenance=dict(ancestor_ready_sha256=s.sha(s.ANCESTOR/'READY.json'),data_sha256=s.sha(s.ROOT/'DATA.json'),ancestor_selection_sha256=s.sha(s.ANCESTOR/'SELECTION_AUDIT.json'),context_count=16,pairs=768,source_selection='all16 unchanged; no outcomes or labels used',exposure='same panel becomes exposed by queued ancestor; not fresh confirmation',original_record_ids_retained_privately=True)
    values={'PLAN.json':rows,'REQUESTS.json':requests,'ORDERED_REQUESTS.json':ordered,'PROMPT_IDS.json':prompts,'UNRELATED_IDS.json':aliases,'PROVENANCE.json':provenance,'COLLISION_AUDIT.json':dict(started_epoch=started,ended_epoch=time.time(),named_sha256={str(x):s.sha(x) for x in named},alias_count=len(alias_set),alias_manifest_collisions=[],seeds=seeds,seed_collisions=[],scope='named MNLI top-level source inventories only; no outputs read'),'CPU_NATIVE.json':dict(requests=48,contexts=16,schemas_unique=16,grammar_arms_identical=True,checks=checks,max_prompt_tokens=max(map(len,prompts.values())),max_prompt_plus_output=max(map(len,prompts.values()))+3072,all_fit8192=all(len(v)+3072<=8192 for v in prompts.values()),request_wire_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in ordered.items()},versions={name:importlib.metadata.version(name) for name in ('vllm','transformers','xgrammar')},dispatch_first_counts=dict(Counter(r['arm'] for r in rows if r['pair_position']==0)),elapsed_seconds=time.time()-started,gpu_calls=0,service_calls=0),'PLANNED_NULL_ENDPOINTS.json':[p.null_row(r,'not yet attempted') for r in rows]}
    assert values['CPU_NATIVE.json']['all_fit8192']
    for name,value in values.items():s.write(s.ROOT/name,value)
def qualify():
    cmd=[str(s.NATIVE),'-m','unittest','-v','test_protocol','test_scoring','test_owner','test_collect'];start=time.time()
    result=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=180,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    number=1
    while (s.ROOT/f'CPU_TESTS_{number:03d}.json').exists():number+=1
    s.write(s.ROOT/f'CPU_TESTS_{number:03d}.json',dict(argv=cmd,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-start,source_sha256={str(p):s.sha(p) for p in s.ROOT.glob('*.py')},gpu_calls=0,service_calls=0));print(result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
def source_closure():
    historical={str(s.SIDE/'root-native-partition-join-v1/READY.json'):'e39c9d619e9ff8e95ca7bf1733cebe575e9ff7dcaabbdb2edb1de9498f30c6c5',str(s.SIDE/'leaf-mnli-shifted-correspondence-v1/READY.json'):'ef47b2576bb530df6aef58301f28d861c4ed278d9e3778bc9cbd23183ff9a5a1',str(s.SIDE/'leaf-mnli-alien-tag-correspondence-v1/READY.json'):'41f74dbe8bee485b553d1804c6d602a36dceb9984c79dda8f69e0dd1e8c0a593'}
    source={};pending=[s.ANCESTOR/'READY.json'];seen=set()
    while pending:
        path=pending.pop()
        if str(path) in seen:continue
        seen.add(str(path));source[str(path)]=s.sha(path)
        if str(path) in historical:
            assert source[str(path)]==historical[str(path)]
            continue
        value=s.read(path)
        for key in ('source_sha256','input_sha256'):
            for pth,pin in value.get(key,{}).items():
                assert s.sha(pth)==pin;source[pth]=pin
                if Path(pth).name.lower().startswith('ready') and Path(pth).suffix=='.json':pending.append(Path(pth))
    return source,historical,sorted(seen)
def seal():
    receipt=sorted(s.ROOT.glob('CPU_TESTS_*.json'))[-1];tests=s.read(receipt);assert tests['returncode']==0
    for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
    source,historical,manifests=source_closure()
    for path in s.ROOT.iterdir():
        if path.is_file() and path!=s.READY_PATH:source[str(path)]=s.sha(path)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,input_sha256={str(p):s.sha(p) for p in s.ROOT.glob('*.json') if p!=s.READY_PATH},model=s.MODEL,adapter=None,planned_endpoints=48,contexts=16,paired_seeds=1,arms=list(p.ARMS),primary='aligned-minus-wrong',secondary='wrong-minus-unrelated; repetition caveat',forced_tag_sequences_fixed=True,complete_sampled_sequences_fixed=False,exposure='all16 reused queued-panel contexts; not fresh confirmation',work_seconds=1080,owned_seconds=1170,outer_seconds=1200,startup_seconds=180,cleanup_seconds=90,outer_margin_seconds=30,workers=4,request_seconds=90,seed_master=p.MASTER,argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],prepared_epoch=time.time(),gpu_calls=0,service_calls=0)
    ready.update(historical_receipts_not_executable_closures=historical,expanded_ready_manifests=manifests)
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(s.sha(s.READY_PATH),ready['identity'],len(source))
if __name__=='__main__':
    import argparse;ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));a=ap.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
    globals()[a.command]()
