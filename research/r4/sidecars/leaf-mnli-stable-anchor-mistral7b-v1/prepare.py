"""CPU-only native Mistral request freeze, qualification, and seal."""
import copy,hashlib,importlib.metadata,json,os,subprocess,time
from pathlib import Path
import xgrammar as xg
import protocol as p,study as s
def freeze(path,value):
 if Path(path).exists():
  if s.read(path)!=value:raise ValueError('frozen artifact differs: '+str(path))
 else:s.write(path,value)
def typed(tokenizer,body):
 from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
 value=ChatCompletionRequest.model_validate(copy.deepcopy(body));assert not value.tools
 return tokenizer.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**value.chat_template_kwargs)
def inputs():
 old_plan=s.read(s.PRIOR/'PLAN.json');old_requests=s.read(s.PRIOR/'REQUESTS.json');chosen=[x for x in old_plan if x['anchor'] in p.ANCHORS];assert len(chosen)==144;plan=[];requests={}
 for position,old in enumerate(chosen):
  row=dict(old);row['source_id']=old['id'];row['id']=s.digest([s.ROOT.name,old['id']]);row['pair_position']=position;plan.append(row);body=copy.deepcopy(old_requests[old['id']]);body['model']=s.MODEL['alias'];body['cache_salt']=s.ROOT.name;requests[row['id']]=body
 for name in ('DATA.json','PUBLIC.json','ALIEN_DICTIONARIES.json','DATASET_MANIFEST.json'):freeze(s.ROOT/name,s.read(s.PRIOR/name))
 tokenizer=s.tokenizer();config=s.read(s.MODEL_PATH/'config.json')
 if config.get('auto_map') or config.get('architectures')!=['MistralForCausalLM'] or config.get('model_type')!='mistral' or config.get('max_position_embeddings',0)<s.MAX_MODEL_LEN:raise ValueError('unexpected model config')
 if tokenizer.eos_token_id!=2 or tokenizer.bos_token_id!=1:raise ValueError('unexpected Mistral terminals')
 prompts={key:typed(tokenizer,body) for key,body in requests.items()};wires={key:s.serialize(body) for key,body in requests.items()}
 compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tokenizer,vocab_size=config['vocab_size']),max_threads=2,cache_enabled=True);checks=[]
 by_source={x['source_id']:x for x in plan}
 for row in plan:
  body=requests[row['id']];source=old_requests[row['source_id']]
  if body['messages']!=source['messages'] or body['structured_outputs']!=source['structured_outputs'] or body['temperature']!=.5 or body['seed']!=row['seed']:raise ValueError('scientific request changed')
  if len(prompts[row['id']])+body['max_tokens']>s.MAX_MODEL_LEN:raise ValueError('Mistral bound exceeded')
  grammar=compiler.compile_json_schema(s.serialize(body['structured_outputs']['json']),any_whitespace=True);matcher=xg.GrammarMatcher(grammar);context=p.contexts()[row['context_index']];good=['neutral']*48 if row['anchor']=='labels_only' else [{'key':key,'label':'neutral'} for key in p.anchor_values(context,row['anchor'])]
  if not matcher.accept_string(s.serialize(good).encode()) or not matcher.is_completed():raise ValueError('grammar rejects canonical output')
  checks.append({'id':row['id'],'arm':row['arm'],'prompt_tokens':len(prompts[row['id']]),'canonical_contract_accepts':True})
 manifest=s.read(s.MODEL_PATH/'ACQUISITION_MANIFEST.json');assert s.sha(s.MODEL_PATH/'ACQUISITION_MANIFEST.json')==s.MODEL['manifest_sha256'] and manifest['revision']==s.MODEL['revision'] and not manifest['remote_code_executed'] and not manifest['duplicate_consolidated_weights_downloaded']
 artifacts={'PLAN.json':plan,'REQUESTS.json':requests,'ORDERED_REQUESTS.json':wires,'PROMPT_IDS.json':prompts,'CPU_NATIVE.json':{'schema':'mistral-7b-native-request-freeze-v1','requests':144,'schemas_compiled':144,'checks':checks,'request_wire_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in wires.items()},'max_prompt_tokens':max(map(len,prompts.values())),'max_prompt_plus_output':max(len(prompts[k])+requests[k]['max_tokens'] for k in requests),'versions':{n:importlib.metadata.version(n) for n in ('vllm','transformers','xgrammar')},'gpu_calls':0,'service_calls':0},'PLANNED_NULL_ENDPOINTS.json':[p.null_row(x,'before service startup') for x in plan],'WEIGHTS.json':{'schema':'released-base-model-binding-v1','checkpoint':s.MODEL,'adapter':None},'MODEL_PROVENANCE.json':{'schema':'local-huggingface-model-provenance-v1','model':s.MODEL,'manifest_sha256':s.sha(s.MODEL_PATH/'ACQUISITION_MANIFEST.json'),'manifest_file_count':len(manifest['files']),'manifest_expected_bytes':manifest['expected_bytes'],'license':manifest['license'],'remote_code_executed':False,'config_sha256':s.sha(s.MODEL_PATH/'config.json'),'tokenizer_config_sha256':s.sha(s.MODEL_PATH/'tokenizer_config.json')},'EOS_DIAGNOSTIC.json':{'tokenizer_class':type(tokenizer).__name__,'eos_token':'</s>','eos_token_id':tokenizer.eos_token_id,'bos_token_id':tokenizer.bos_token_id,'qwen_terminal_ids_prohibited':[151643,151645],'trust_remote_code':False,'config_auto_map':config.get('auto_map'),'chat_template_probe_ids':tokenizer.apply_chat_template([{'role':'system','content':'system'},{'role':'user','content':'hello'}],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False)}}
 for name,value in artifacts.items():freeze(s.ROOT/name,value)
def qualify():
 cmd=[str(s.NATIVE),'-m','pytest','-q','test_cross_family.py'];started=time.time();result=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=300,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'});freeze(s.ROOT/'CPU_TESTS.json',{'argv':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'elapsed_seconds':time.time()-started,'source_sha256':{str(x):s.sha(x) for x in s.ROOT.glob('*.py')},'gpu_calls':0,'service_calls':0});print(result.stdout,result.stderr)
 if result.returncode:raise SystemExit(result.returncode)
def seal():
 tests=s.read(s.ROOT/'CPU_TESTS.json');assert tests['returncode']==0
 for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
 source_names=('study.py','protocol.py','scoring.py','collect.py','service.py','service_wrapper.py','owner.py','prepare.py','test_cross_family.py','DESIGN.md');input_names=('PLAN.json','REQUESTS.json','ORDERED_REQUESTS.json','PROMPT_IDS.json','CPU_NATIVE.json','DATA.json','PUBLIC.json','ALIEN_DICTIONARIES.json','DATASET_MANIFEST.json','WEIGHTS.json','MODEL_PROVENANCE.json','EOS_DIAGNOSTIC.json','PLANNED_NULL_ENDPOINTS.json');ready={'schema':'leaf-mnli-stable-anchor-mistral7b-ready-v1','status':'CPU_READY_FOR_MAIN_ACCEPTANCE','planned_endpoints':144,'contexts':16,'anchors':list(p.ANCHORS),'relations':list(p.RELATIONS),'model':s.MODEL,'adapter':None,'temperature':.5,'max_model_len':s.MAX_MODEL_LEN,'workers':4,'request_seconds':90,'outer_seconds':2400,'work_seconds':2250,'owned_seconds':2370,'gpu_launch_authority':'MAIN only','source_sha256':{str(s.ROOT/n):s.sha(s.ROOT/n) for n in source_names},'input_sha256':{str(s.ROOT/n):s.sha(s.ROOT/n) for n in input_names},'test_receipt_sha256':s.sha(s.ROOT/'CPU_TESTS.json'),'ancestor_sha256':{str(s.PRIOR/'READY.json'):s.sha(s.PRIOR/'READY.json'),str(s.MODEL_PATH/'ACQUISITION_MANIFEST.json'):s.sha(s.MODEL_PATH/'ACQUISITION_MANIFEST.json')},'argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],'gpu_calls':0,'service_calls':0};ready['identity']=s.digest(ready);freeze(s.ROOT/'READY.json',ready);s.verify();print(s.sha(s.ROOT/'READY.json'),ready['identity'])
if __name__=='__main__':
 import sys
 if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
 globals()[sys.argv[1]]()
