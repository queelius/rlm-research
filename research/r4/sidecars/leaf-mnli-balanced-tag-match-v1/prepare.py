import copy,hashlib,importlib.metadata,json,os,subprocess,time
from pathlib import Path
import protocol as p,study as s
import xgrammar as xg
def typed(tok,b):
 from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
 v=ChatCompletionRequest.model_validate(copy.deepcopy(b));return tok.apply_chat_template(b['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**v.chat_template_kwargs)
def inputs():
 cs=p.contexts();sets={str(c['index']):{x:p.tags(c,x) for x in 'AB'} for c in cs};public={r['id'] for c in cs for r in c['records']};refs={x for c in cs for x in p.visible_ids(c,'alien')+p.visible_ids(c,'aligned')};alltags={x for v in sets.values() for a in v.values() for x in a}
 assert len(alltags)==1536 and not alltags&(public|refs) and all(not set(v['A'])&set(v['B']) for v in sets.values())
 plan=p.plan();req={r['id']:p.request(cs[r['context_index']],r) for r in plan};tok=s.tokenizer();prom={k:typed(tok,v) for k,v in req.items()};assert max(map(len,prom.values()))+3072<=8192
 wires={k:s.serialize(v) for k,v in req.items()};config=s.read(Path(s.MODEL['path'])/'config.json');vocabulary=config.get('text_config',config)['vocab_size'];compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocabulary),max_threads=2,cache_enabled=True);checks=[]
 for row in plan:
  body=req[row['id']];grammar=compiler.compile_json_schema(s.serialize(body['structured_outputs']['json']),any_whitespace=True);matcher=xg.GrammarMatcher(grammar);good=[{'answer_tag':tag,'label':'neutral'} for tag in p.tags(cs[row['context_index']],row['output_set'])];assert matcher.accept_string(s.serialize(good).encode()) and matcher.is_completed();checks.append({'id':row['id'],'arm':row['arm'],'prompt_tokens':len(prom[row['id']]),'canonical_contract_accepts':True})
 vals={'PLAN.json':plan,'REQUESTS.json':req,'ORDERED_REQUESTS.json':wires,'PROMPT_IDS.json':prom,'CPU_NATIVE.json':{'requests':192,'schemas_compiled':192,'checks':checks,'max_prompt_tokens':max(map(len,prom.values())),'max_prompt_plus_output':max(map(len,prom.values()))+3072,'request_wire_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in wires.items()},'versions':{n:importlib.metadata.version(n) for n in ('vllm','transformers','xgrammar')},'gpu_calls':0,'service_calls':0},'PLANNED_NULL_ENDPOINTS.json':[p.null_row(r,'not attempted') for r in plan],'TAG_SETS.json':sets,'DATA.json':{'contexts':cs},'DATASET_MANIFEST.json':s.read(s.PRIOR/'DATASET_MANIFEST.json'),'SOURCE_PINS.json':{'prior_ready':s.sha(s.PRIOR/'READY.json'),'prior_data':s.sha(s.PRIOR/'DATA.json'),'prior_aliens':s.sha(s.PRIOR/'ALIEN_DICTIONARIES.json'),'idea':s.sha(s.ROOT.parents[1]/'ideas/2026-09-10-do-the-tags-have-to-match.md')}}
 for n,v in vals.items():s.write(s.ROOT/n,v)
def qualify():
 cmd=[str(s.NATIVE),'-m','pytest','-q','test_runtime.py'];started=time.time();r=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=300,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'});s.write(s.ROOT/'CPU_TESTS.json',{'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.time()-started,'source_sha256':{str(x):s.sha(x) for x in s.ROOT.glob('*.py')},'gpu_calls':0,'service_calls':0});print(r.stdout,r.stderr)
 if r.returncode:raise SystemExit(r.returncode)
def seal():
 tests=s.read(s.ROOT/'CPU_TESTS.json');assert tests['returncode']==0
 for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
 src={str(x):s.sha(x) for x in s.ROOT.iterdir() if x.is_file() and x.name not in ('READY.json','CPU_TESTS.json')};src[str(s.PRIOR/'READY.json')]=s.sha(s.PRIOR/'READY.json');inp={str(s.ROOT/n):s.sha(s.ROOT/n) for n in ('PLAN.json','REQUESTS.json','ORDERED_REQUESTS.json','PROMPT_IDS.json','CPU_NATIVE.json','PLANNED_NULL_ENDPOINTS.json','TAG_SETS.json','DATA.json','DATASET_MANIFEST.json','SOURCE_PINS.json')};r={'schema':'leaf-mnli-balanced-tag-match-ready-v1','status':'CPU_READY_FOR_MAIN_ACCEPTANCE','planned_endpoints':192,'contexts':16,'cells':list(p.CELLS),'relations':list(p.RELATIONS),'master':p.MASTER,'primary':'late mean(match AA,BB)-mean(nonmatch AB,BA), pooled over relations and contexts','outer_seconds':1800,'owned_seconds':1770,'work_seconds':1650,'workers':4,'request_seconds':90,'model':s.MODEL,'adapter':None,'source_sha256':src,'input_sha256':inp,'test_receipt_sha256':s.sha(s.ROOT/'CPU_TESTS.json'),'argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],'gpu_calls':0,'service_calls':0};r['identity']=s.digest(r);s.write(s.ROOT/'READY.json',r);s.verify();print(s.sha(s.ROOT/'READY.json'),r['identity'])
if __name__=='__main__':
 import sys
 if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
 globals()[sys.argv[1]]()
