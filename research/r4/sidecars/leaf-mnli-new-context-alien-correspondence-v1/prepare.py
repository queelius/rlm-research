"""CPU-only input freeze, qualification and READY seal."""
import copy,hashlib,importlib.metadata,importlib.util,json,os,subprocess,time
from pathlib import Path
import protocol as p,study as s

PARQUET=Path('/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2/validation_matched.parquet')
CHECK=s.SIDE.parent/'analyses/mnli-new-context-feasibility-2026-09-10/check_v2.py'
CHECK_PIN='a2760181e19ebed8e943358ac709585ef444d4df11783fdb96a161e4bd77f937'
def selection_module():
    if s.sha(CHECK)!=CHECK_PIN:raise ValueError('selection source changed')
    spec=importlib.util.spec_from_file_location('new_context_alien_selection',CHECK);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.MASTER=p.MASTER;return m
def typed(tok,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value=ChatCompletionRequest.model_validate(copy.deepcopy(body));assert not value.tools
    return tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**value.chat_template_kwargs)
def inputs():
    import pyarrow.parquet as pq
    import xgrammar as xg
    started=time.time();f=selection_module();scan_start=time.time();excluded=set(s.read(f.BASE/'EXPOSURE.json')['exact_text_hits']);named=[];visible=set()
    for directory in sorted(s.SIDE.glob('*mnli*')):
        if directory==s.ROOT:continue
        for name in ('DATA.json','PUBLIC.json','PLAN.json','REQUESTS.json','READY.json','READY_v2.json'):
            path=directory/name
            if not path.exists():continue
            named.append(path)
            if name not in ('DATA.json','PUBLIC.json'):continue
            value=s.read(path);contexts=value.get('contexts',value) if isinstance(value,dict) else value
            for context in contexts:
                for row in context['records']:
                    for field in ('premise','hypothesis'):excluded.add(f.group(row[field]))
                    visible.add(row['id'])
    if s.sha(PARQUET)!='350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186':raise ValueError('source parquet changed')
    source_rows=pq.read_table(PARQUET).to_pylist();contexts,eligible,conflicts=f.select(source_rows,excluded)
    mutated=[{**row,'label':int(f.digest([p.MASTER,'label-mutation',i]),16)%3} for i,row in enumerate(source_rows)];changed,_,_=f.select(mutated,excluded)
    label_invariant=f.public(changed)==f.public(contexts)
    prior_groups={group for path in named if path.name in ('DATA.json','PUBLIC.json') for context in ((s.read(path).get('contexts',s.read(path))) if isinstance(s.read(path),dict) else s.read(path)) for group in context.get('premise_groups',[])}
    overlap=sorted(prior_groups&{group for context in contexts for group in context['premise_groups']})
    if not label_invariant or overlap or conflicts:raise ValueError('selection invariant')
    s.write(s.ROOT/'DATA.json',{'contexts':contexts});s.write(s.ROOT/'PUBLIC.json',[{'index':c['index'],'genre':c['genre'],'records':[{k:r[k] for k in ('id','premise','hypothesis')} for r in c['records']]} for c in contexts])
    s.write(s.ROOT/'SELECTION_AUDIT.json',{'scan_started_epoch':scan_start,'scan_ended_epoch':time.time(),'master':p.MASTER,'named_paths':[str(x) for x in named],'named_sha256':{str(x):s.sha(x) for x in named},'excluded_normalized_text_hashes':len(excluded),'eligible_premise_groups':eligible,'source_rows':len(source_rows),'selected_contexts':16,'selected_premise_groups':256,'prior_selected_overlap':overlap,'label_mutation_invariant':label_invariant,'source_parquet_sha256':s.sha(PARQUET),'scope':'named inventories; not globally or pretraining unseen'})
    rows=p.plan();tok=s.tokenizer();requests={r['id']:p.request(contexts[r['context_index']],r) for r in rows};prompts={k:typed(tok,v) for k,v in requests.items()};ordered={k:s.serialize(v) for k,v in requests.items()}
    aliases={x for values in p.alien_dictionary().values() for x in values};manifest='\n'.join(path.read_text(errors='replace') for path in named);alias_collisions=sorted(aliases&visible);text_collisions=sorted(x for x in aliases if x in manifest);seeds=sorted({r['seed'] for r in rows});seed_collisions=sorted(seed for seed in seeds if str(seed) in manifest)
    if len(aliases)!=768 or alias_collisions or text_collisions or seed_collisions:raise ValueError('alias/seed collision')
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=s.read(Path(s.MODEL['path'])/'config.json').get('text_config',s.read(Path(s.MODEL['path'])/'config.json'))['vocab_size']),max_threads=2,cache_enabled=True);checks=[]
    for ci,context in enumerate(contexts):
        for arm in p.ARMS:
            grammar=compiler.compile_json_schema(s.serialize(p.schema(context,arm)['json']),any_whitespace=True)
            def accepts(value):matcher=xg.GrammarMatcher(grammar);return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
            tags=p.expected_tags(context,arm)
            for label in p.LABELS:assert accepts([{'tag':tag,'label':label} for tag in tags])
            wrong=[{'tag':tag,'label':p.LABELS[i%3]} for i,tag in enumerate(tags)];wrong[0]['tag']=tags[1];assert not accepts(wrong)
            checks.append({'context':ci,'arm':arm,'schema_sha256':s.digest(p.schema(context,arm))})
    values={'PLAN.json':rows,'REQUESTS.json':requests,'ORDERED_REQUESTS.json':ordered,'PROMPT_IDS.json':prompts,'ALIEN_DICTIONARIES.json':p.alien_dictionary(),'COLLISION_AUDIT.json':{'scan_started_epoch':scan_start,'scan_ended_epoch':time.time(),'named_paths':[str(x) for x in named],'named_sha256':{str(x):s.sha(x) for x in named},'visible_ids':len(visible),'alien_ids':len(aliases),'alien_visible_collisions':alias_collisions,'alien_manifest_text_collisions':text_collisions,'seeds':seeds,'seed_collisions':seed_collisions,'scope':'named inventory only'},'CPU_NATIVE.json':{'requests':48,'schemas':48,'checks':checks,'max_prompt_tokens':max(map(len,prompts.values())),'max_prompt_plus_output':max(map(len,prompts.values()))+3072,'all_fit8192':all(len(v)+3072<=8192 for v in prompts.values()),'request_wire_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in ordered.items()},'versions':{name:importlib.metadata.version(name) for name in ('vllm','transformers','xgrammar')},'elapsed_seconds':time.time()-started,'gpu_calls':0,'service_calls':0}}
    for name,value in values.items():s.write(s.ROOT/name,value)
    s.write(s.ROOT/'PLANNED_NULL_ENDPOINTS.json',[p.null_row(row,'not yet attempted') for row in rows])
def qualify():
    started=time.time();cmd=[str(s.NATIVE),'-m','unittest','-v','test_science','test_inventory','test_owner','test_collect'];result=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=180,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    candidates=['CPU_TESTS.json','CPU_TESTS_V2.json','CPU_TESTS_V3.json'];target=next(s.ROOT/name for name in candidates if not (s.ROOT/name).exists())
    s.write(target,{'argv':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'elapsed_seconds':time.time()-started,'source_sha256':{str(x):s.sha(x) for x in s.ROOT.glob('*.py')},'gpu_calls':0,'service_calls':0});print(result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
def seal():
    candidates=[s.ROOT/name for name in ('CPU_TESTS.json','CPU_TESTS_V2.json','CPU_TESTS_V3.json') if (s.ROOT/name).exists()];tests=s.read(candidates[-1]);assert tests['returncode']==0
    for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
    source={str(s.NEW/'READY.json'):s.sha(s.NEW/'READY.json'),str(s.ALIEN/'READY_v2.json'):s.sha(s.ALIEN/'READY_v2.json'),str(CHECK):s.sha(CHECK)}
    for path in s.ROOT.iterdir():
        if path.is_file() and path!=s.READY_PATH:source[str(path)]=s.sha(path)
    input_names=('DATA.json','PUBLIC.json','SELECTION_AUDIT.json','PLAN.json','REQUESTS.json','ORDERED_REQUESTS.json','PROMPT_IDS.json','ALIEN_DICTIONARIES.json','COLLISION_AUDIT.json','CPU_NATIVE.json','PLANNED_NULL_ENDPOINTS.json')
    inputs={str(s.ROOT/name):s.sha(s.ROOT/name) for name in input_names}
    ready={'status':'CPU_READY_FOR_MAIN_ACCEPTANCE','source_sha256':source,'input_sha256':inputs,'model':s.MODEL,'adapter':None,'planned_endpoints':48,'contexts':16,'paired_seeds':1,'arms':list(p.ARMS),'new_context_boundary':'named MNLI inventories only; not globally/pretraining unseen','decoder':'exact_requested_tag_all_arms','work_seconds':1080,'owned_seconds':1170,'outer_seconds':1200,'startup_seconds':180,'cleanup_seconds':90,'outer_margin_seconds':30,'workers':4,'request_seconds':90,'seed_master':p.MASTER,'argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],'prepared_epoch':time.time(),'gpu_calls':0,'service_calls':0};ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(s.sha(s.READY_PATH),ready['identity'],len(source),len(inputs))
if __name__=='__main__':
    import argparse;ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));a=ap.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
    globals()[a.command]()
