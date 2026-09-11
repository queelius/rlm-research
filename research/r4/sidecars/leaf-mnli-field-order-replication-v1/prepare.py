"""CPU-only context selection, request qualification, and READY seal."""
import collections,copy,hashlib,importlib.metadata,json,os,subprocess,time,unicodedata
from pathlib import Path
import protocol as p,study as s

PARQUET=Path('/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2/validation_matched.parquet')
CACHE=PARQUET.parent;PARQUET_SHA='350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186'
def parent_ready():return s.FIELD_ORDER/'READY_v2.json'
def norm(text):return ' '.join(unicodedata.normalize('NFKC',text).casefold().split())
def group(text):return hashlib.sha256(norm(text).encode()).hexdigest()
def pair(row):return s.digest([norm(row['premise']),norm(row['hypothesis'])])
def contexts_from(value):
    if isinstance(value,dict):value=value.get('contexts',value.get('groups',[]))
    return value if isinstance(value,list) else []
def declared_groups(value):
    result=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('premise_group','source_group') and isinstance(item,str) and len(item)==64:result.add(item)
            elif key in ('premise_groups','source_groups') and isinstance(item,list):result.update(x for x in item if isinstance(x,str) and len(x)==64)
            result.update(declared_groups(item))
    elif isinstance(value,list):
        for item in value:result.update(declared_groups(item))
    return result
def named_inventory():
    paths=[];excluded=set(s.read(s.BASE/'EXPOSURE.json')['exact_text_hits']);premise_groups=set()
    for directory in sorted(s.SIDE.glob('*mnli*')):
        if directory==s.ROOT:continue
        for path in sorted(directory.iterdir()):
            if not path.is_file() or not (path.name.startswith(('DATA','PUBLIC','GROUPS','PLAN')) and path.suffix=='.json'):continue
            paths.append(path);value=s.read(path);premise_groups.update(declared_groups(value))
            for context in contexts_from(value):
                if not isinstance(context,dict):continue
                premise_groups.update(context.get('premise_groups',[]))
                for row in context.get('records',[]):
                    if isinstance(row,dict) and isinstance(row.get('premise'),str):
                        premise_groups.add(group(row['premise']));excluded.add(group(row['premise']))
                    if isinstance(row,dict) and isinstance(row.get('hypothesis'),str):excluded.add(group(row['hypothesis']))
    excluded.update(premise_groups)
    return paths,excluded,premise_groups
def eligible_groups(rows,excluded):
    dedup=collections.defaultdict(list)
    for index,row in enumerate(rows):dedup[pair(row)].append((index,row))
    groups=collections.defaultdict(list);conflicts=[]
    for key,values in dedup.items():
        if len({r['label'] for _,r in values})!=1:conflicts.append(key);continue
        index,row=min(values)
        if row['label'] not in (0,1,2):continue
        groups[group(row['premise'])].append((key,index,row))
    eligible={}
    for key,values in groups.items():
        if key in excluded or len(values)!=3 or {row['label'] for _,_,row in values}!={0,1,2}:continue
        if len({row['genre'] for _,_,row in values})!=1 or any(group(row['hypothesis']) in excluded for _,_,row in values):continue
        eligible[key]=values
    return eligible,conflicts
def select(rows,excluded):
    eligible,conflicts=eligible_groups(rows,excluded);contexts=[];counts={};ranked_receipt={}
    for genre in p.GENRES:
        ranked=sorted((key for key,values in eligible.items() if values[0][2]['genre']==genre),key=lambda key:s.digest([p.MASTER,'select',genre,key]))
        counts[genre]=len(ranked);ranked_receipt[genre]=ranked[:64]
        if len(ranked)<64:return None,counts,conflicts,ranked_receipt
        for block in range(4):
            chosen=ranked[block*16:(block+1)*16];records=[];ci=len(contexts)
            for round_index in range(3):
                for key in sorted(chosen,key=lambda key:s.digest([p.MASTER,'display',ci,round_index,key])):
                    pair_id,index,row=sorted(eligible[key])[round_index]
                    records.append(dict(id='m'+pair_id[:12],premise=row['premise'],hypothesis=row['hypothesis'],gold_label=p.LABELS[row['label']],premise_group=key,pair_group=pair_id,source_row=index,original_pairID=row['pairID'],original_promptID=row['promptID']))
            contexts.append(dict(index=ci,genre=genre,premise_groups=chosen,records=records))
    return contexts,counts,conflicts,ranked_receipt
def public(contexts):return [{'index':c['index'],'genre':c['genre'],'premise_groups':c['premise_groups'],'records':[{k:r[k] for k in ('id','premise','hypothesis')} for r in c['records']]} for c in contexts]
def make_aliens(contexts,tok):
    used={r['id'] for c in contexts for r in c['records']};result={}
    for ci,c in enumerate(contexts):
        values=[]
        for position,target in enumerate([r['id'] for r in c['records']][17:]+[r['id'] for r in c['records']][:17]):
            wanted=len(tok.encode(target,add_special_tokens=False));nonce=0
            while True:
                candidate='m'+hashlib.sha256(f'field-order-replication:{p.MASTER}:{ci}:{position}:{nonce}'.encode()).hexdigest()[:12]
                if candidate not in used and len(tok.encode(candidate,add_special_tokens=False))==wanted:break
                nonce+=1
            used.add(candidate);values.append(candidate)
        result[str(ci)]=values
    return result
def typed(tok,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value=ChatCompletionRequest.model_validate(copy.deepcopy(body));assert not value.tools
    return tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**value.chat_template_kwargs)

def inputs():
    import pyarrow.parquet as pq
    if s.sha(PARQUET)!=PARQUET_SHA:raise ValueError('source parquet changed')
    started=time.time();paths,excluded,prior_groups=named_inventory();rows=pq.read_table(PARQUET).to_pylist()
    contexts,counts,conflicts,ranked=select(rows,excluded)
    if contexts is None:
        s.write(s.ROOT/'INSUFFICIENT_POOL.json',dict(master=p.MASTER,eligible_by_genre=counts,required_by_genre=64,named_sha256={str(x):s.sha(x) for x in paths},source_parquet_sha256=s.sha(PARQUET),preserved=True))
        raise ValueError('insufficient eligible pool; preserved without replacement')
    rotated=[{**row,'label':(row['label']+1)%3 if row['label'] in (0,1,2) else row['label']} for row in rows]
    changed,_,_,changed_ranked=select(rotated,excluded);invariant=changed is not None and public(changed)==public(contexts) and ranked==changed_ranked
    selected={g for c in contexts for g in c['premise_groups']};overlap=sorted(selected&prior_groups)
    if not invariant or overlap or conflicts:raise ValueError('selection invariant')
    s.write(s.ROOT/'DATA.json',{'contexts':contexts});s.write(s.ROOT/'PUBLIC.json',public(contexts))
    s.write(s.ROOT/'SELECTION_AUDIT.json',dict(master=p.MASTER,source_rows=len(rows),source_parquet_sha256=s.sha(PARQUET),named_paths=[str(x) for x in paths],named_sha256={str(x):s.sha(x) for x in paths},excluded_premise_groups=sorted(prior_groups),excluded_normalized_text_hashes=len(excluded),eligible_by_genre=counts,selected_contexts=16,selected_premise_groups=256,prior_selected_overlap=overlap,first_ranked_groups_selected=all([g for c in contexts if c['genre']==genre for g in c['premise_groups']]==ranked[genre] for genre in p.GENRES),eligibility_uses_labels=True,eligibility_rule='exactly three deduplicated pairs with labels {0,1,2}',ranking_uses_labels=False,label_mutation_ranking_invariant=invariant,pair_conflicts=conflicts,scope='all named DATA/PUBLIC/GROUPS/PLAN inventories; not globally or pretraining unseen'))
    tok=s.tokenizer();s.write(s.ROOT/'ALIEN_DICTIONARIES.json',make_aliens(contexts,tok))
    requests={r['id']:p.request(contexts[r['context_index']],r) for r in p.plan()};wires={k:s.serialize(v) for k,v in requests.items()};prompts={k:typed(tok,v) for k,v in requests.items()}
    import xgrammar as xg
    config=s.read(Path(s.MODEL['path'])/'config.json');vocab=config.get('text_config',config)['vocab_size'];compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocab),max_threads=2,cache_enabled=True);checks=[]
    for row in p.plan():
        body=requests[row['id']];grammar=compiler.compile_json_schema(s.serialize(body['structured_outputs']['json']),any_whitespace=True)
        def accepts(value):matcher=xg.GrammarMatcher(grammar);return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
        tags=p.requested_tags(contexts[row['context_index']]);good=[{k:({'tag':t,'label':'neutral'})[k] for k in p.field_order(row['arm'])} for t in tags]
        assert accepts(good) and not accepts([dict(reversed(list(v.items()))) for v in good]) and len(prompts[row['id']])+3072<=8192
        checks.append(dict(id=row['id'],arm=row['arm'],context_index=row['context_index'],prompt_tokens=len(prompts[row['id']]),correct_order_accepts=True,opposite_order_rejected=True))
    values={'PLAN.json':p.plan(),'REQUESTS.json':requests,'ORDERED_REQUESTS.json':wires,'PROMPT_IDS.json':prompts,'CPU_NATIVE.json':dict(requests=96,schemas_compiled=96,schema_checks=checks,max_prompt_tokens=max(map(len,prompts.values())),max_prompt_plus_output=max(map(len,prompts.values()))+3072,all_fit8192=all(len(v)+3072<=8192 for v in prompts.values()),request_wire_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in wires.items()},versions={n:importlib.metadata.version(n) for n in ('vllm','transformers','xgrammar')},elapsed_seconds=time.time()-started,gpu_calls=0,service_calls=0),'PLANNED_NULL_ENDPOINTS.json':[p.null_row(r,'not attempted') for r in p.plan()],'DATASET_MANIFEST.json':dict(dataset='nyu-mll/multi_nli',revision='da70db2af9d09693783c3320c4249840212ee221',split='validation_matched',license='Mixed OANC permissive terms / CC-BY-3.0 / CC-BY-SA-3.0 / public-domain fiction; see pinned card',parquet_sha256=s.sha(PARQUET),readme_sha256=s.sha(CACHE/'README.md'),acquisition_sha256=s.sha(CACHE/'ACQUISITION.json'),retrieved_utc=s.read(CACHE/'ACQUISITION.json')['retrieved_utc'])}
    for name,value in values.items():s.write(s.ROOT/name,value)
    print(dict(contexts=16,premise_groups=256,requests=96,eligible_by_genre=counts,max_prompt=max(map(len,prompts.values()))))
def qualify():
    cmd=[str(s.NATIVE),'-m','pytest','-q','test_science.py','test_runtime.py'];started=time.time();result=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=240,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    s.write(s.ROOT/'CPU_TESTS.json',dict(argv=cmd,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started,source_sha256={str(x):s.sha(x) for x in s.ROOT.glob('*.py')},gpu_calls=0,service_calls=0));print(result.stdout,result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
def seal():
    tests=s.read(s.ROOT/'CPU_TESTS.json');assert tests['returncode']==0
    for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
    input_names=('DATA.json','PUBLIC.json','SELECTION_AUDIT.json','ALIEN_DICTIONARIES.json','PLAN.json','REQUESTS.json','ORDERED_REQUESTS.json','PROMPT_IDS.json','CPU_NATIVE.json','PLANNED_NULL_ENDPOINTS.json','DATASET_MANIFEST.json')
    inputs={str(s.ROOT/name):s.sha(s.ROOT/name) for name in input_names};source={str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and path!=s.READY_PATH};source[str(parent_ready())]=s.sha(parent_ready())
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',model=s.MODEL,adapter=None,planned_endpoints=96,contexts=16,paired_seeds=1,arms=list(p.ARMS),primary=p.PRIMARY,gate=p.GATE,new_context_boundary='all named DATA/PUBLIC/GROUPS/PLAN inventories; not globally/pretraining unseen',dataset=s.read(s.ROOT/'DATASET_MANIFEST.json'),decoder='exact_requested_tag_all_arms',work_seconds=1680,owned_seconds=1770,outer_seconds=1800,startup_seconds=180,cleanup_seconds=90,outer_margin_seconds=30,workers=4,request_seconds=90,seed_master=p.MASTER,argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],source_sha256=source,input_sha256=inputs,prepared_epoch=time.time(),gpu_calls=0,service_calls=0);ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(s.sha(s.READY_PATH),ready['identity'])
if __name__=='__main__':
    ap=__import__('argparse').ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));args=ap.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
    globals()[args.command]()
