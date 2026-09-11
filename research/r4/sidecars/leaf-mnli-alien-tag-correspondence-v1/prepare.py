import copy,hashlib,importlib.metadata,json,os,subprocess,time
from pathlib import Path
import protocol as p,study as s
def typed(tok,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value=ChatCompletionRequest.model_validate(copy.deepcopy(body));assert not value.tools
    return tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**value.chat_template_kwargs)
def inputs():
    import xgrammar as xg
    started=time.time();ctx=p.contexts();rows=p.plan();tok=s.tokenizer();requests={r['id']:p.request(ctx[r['context_index']],r) for r in rows};prompts={k:typed(tok,v) for k,v in requests.items()}
    scan_start=time.time();named=[s.BASE/'DATA.json',s.SOURCE/'PLAN.json',s.SOURCE/'REQUESTS.json',s.SIDE/'leaf-mnli-shifted-correspondence-v1/PLAN.json',s.SIDE/'leaf-mnli-shifted-correspondence-v1/REQUESTS.json']
    visible={r['id'] for c in ctx for r in c['records']};aliens={x for values in p.alien_dictionary().values() for x in values};collisions=sorted(visible&aliens)
    text='\n'.join(path.read_text() for path in named);manifest_collisions=sorted(x for x in aliens if x in text);new_seeds=sorted({r['seed'] for r in rows});seed_collisions=sorted(x for x in new_seeds if str(x) in text);scan_end=time.time()
    if collisions or manifest_collisions or seed_collisions:raise ValueError('alien/seed collision')
    config=s.read(Path(s.MODEL['path'])/'config.json');vocab=config.get('text_config',config)['vocab_size'];compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocab),max_threads=2,cache_enabled=True);checks=[]
    for ci,c in enumerate(ctx):
        for arm in p.ARMS:
            grammar=compiler.compile_json_schema(s.serialize(p.schema(c,arm)['json']),any_whitespace=True)
            def accepts(v):m=xg.GrammarMatcher(grammar);return m.accept_string(s.serialize(v).encode()) and m.is_completed()
            tags=p.expected_tags(c,arm)
            for label in p.LABELS:assert accepts([{'tag':t,'label':label} for t in tags])
            wrong=[{'tag':t,'label':p.LABELS[i%3]} for i,t in enumerate(tags)];wrong[0]['tag']=tags[1];assert not accepts(wrong)
            checks.append({'context':ci,'arm':arm,'schema_sha256':s.digest(p.schema(c,arm))})
    ordered={k:s.serialize(v) for k,v in requests.items()}
    values={'PLAN.json':rows,'REQUESTS.json':requests,'ORDERED_REQUESTS.json':ordered,'PROMPT_IDS.json':prompts,'ALIEN_DICTIONARIES.json':p.alien_dictionary(),'COLLISION_AUDIT.json':{'scan_started_epoch':scan_start,'scan_ended_epoch':scan_end,'named_paths':[str(x) for x in named],'named_path_sha256':{str(x):s.sha(x) for x in named},'visible_public_ids':len(visible),'alien_ids_total':len(aliens),'collisions':collisions,'manifest_text_collisions':manifest_collisions,'new_seeds':new_seeds,'seed_collisions':seed_collisions,'scope':'named files only; no globally-unseen claim'},'CPU_NATIVE.json':{'requests':48,'schemas':24,'checks':checks,'max_prompt_plus_output':max(map(len,prompts.values()))+3072,'request_wire_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in ordered.items()},'versions':{n:importlib.metadata.version(n) for n in ('vllm','transformers','xgrammar')},'elapsed_seconds':time.time()-started,'gpu_calls':0,'service_calls':0}}
    for name,value in values.items():s.write(s.ROOT/name,value)
def qualify():
    started=time.time();cmd=[str(s.NATIVE),'-m','unittest','-v','test_science','test_scoring','test_owner','test_collect'];result=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    s.write(s.ROOT/'CPU_TESTS.json',{'argv':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'elapsed_seconds':time.time()-started,'source_sha256':{str(x):s.sha(x) for x in s.ROOT.glob('*.py')},'gpu_calls':0,'service_calls':0});print(result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
def seal():
    tests=s.read(s.ROOT/'CPU_TESTS.json');assert tests['returncode']==0
    for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
    inherited=s.read(s.SOURCE/'READY.json');source=dict(inherited['source_sha256']);source[str(s.SOURCE/'READY.json')]=s.sha(s.SOURCE/'READY.json')
    for path in s.ROOT.iterdir():
        if path.is_file() and path!=s.READY_PATH:source[str(path)]=s.sha(path)
    inputs={str(path):s.sha(path) for path in (s.ROOT/'PLAN.json',s.ROOT/'REQUESTS.json',s.ROOT/'ORDERED_REQUESTS.json',s.ROOT/'PROMPT_IDS.json',s.ROOT/'ALIEN_DICTIONARIES.json',s.ROOT/'COLLISION_AUDIT.json',s.ROOT/'CPU_NATIVE.json')}
    ready={'status':'CPU_READY_FOR_MAIN_ACCEPTANCE','source_sha256':source,'input_sha256':inputs,'model':s.MODEL,'adapter':None,'planned_endpoints':48,'contexts':8,'paired_seeds':2,'arms':list(p.ARMS),'research_exposed_panel':True,'decoder':'exact_requested_tag_all_arms','work_seconds':1080,'owned_seconds':1170,'outer_seconds':1200,'startup_seconds':180,'cleanup_seconds':90,'outer_margin_seconds':30,'workers':4,'request_seconds':90,'seed_master':p.MASTER,'argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],'prepared_epoch':time.time(),'gpu_calls':0,'service_calls':0};ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(s.sha(s.READY_PATH),ready['identity'],len(source),len(inputs))
if __name__=='__main__':
    import argparse;ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));a=ap.parse_args();
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
    globals()[a.command]()
