import asyncio,importlib.machinery as machinery,importlib.util as util,json,os,subprocess,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch
import httpx,pytest
ROOT=Path(__file__).resolve().parent;PRIOR=ROOT.parent/'leaf-mnli-stable-anchor-vs-sequence-counting-v1';sys.path.insert(0,str(ROOT))

def test_exact_144_frozen_scientific_subset_and_mistral_template():
 import protocol as p,study as s
 plan=s.read(ROOT/'PLAN.json');requests=s.read(ROOT/'REQUESTS.json');old={x['id']:x for x in s.read(PRIOR/'PLAN.json')};old_requests=s.read(PRIOR/'REQUESTS.json');assert len(plan)==144 and {x['anchor'] for x in plan}==set(p.ANCHORS)
 tokenizer=s.tokenizer();assert tokenizer.eos_token_id==2 and tokenizer.bos_token_id==1 and s.MODEL['revision']=='c170c708c41dac9275d15a8fff4eca08d52bab71'
 for row in plan:
  body=requests[row['id']];source=old_requests[row['source_id']];assert body['messages']==source['messages'] and body['structured_outputs']==source['structured_outputs'];assert body['temperature']==.5 and body['seed']==old[row['source_id']]['seed'];assert body['model']==s.MODEL['alias']
 assert max(len(x) for x in s.read(ROOT/'PROMPT_IDS.json').values())+3072<=s.MAX_MODEL_LEN

def test_native_auth_uses_mistral_eos_not_qwen_constant():
 import protocol as p,scoring,study as s
 row=next(x for x in p.plan() if x['anchor']=='labels_only');context=p.contexts()[row['context_index']];body=s.read(ROOT/'REQUESTS.json')[row['id']];prompt=s.read(ROOT/'PROMPT_IDS.json')[row['id']];content=s.serialize([x['gold_label'] for x in context['records']]);tok=s.tokenizer();tokens=tok.encode(content,add_special_tokens=False)+[tok.eos_token_id]
 raw={'model':body['model'],'prompt_token_ids':prompt,'choices':[{'index':0,'message':{'role':'assistant','content':content,'tool_calls':None},'finish_reason':'stop','token_ids':tokens}],'usage':{'prompt_tokens':len(prompt),'completion_tokens':len(tokens),'total_tokens':len(prompt)+len(tokens)}}
 message,_,_=scoring.verified_response(raw,prompt,tok);assert message['content']==content and tokens[-1]==2
 bad=json.loads(json.dumps(raw));bad['choices'][0]['token_ids'][-1]=151645
 with pytest.raises((ValueError,IndexError,OverflowError)):scoring.verified_response(bad,prompt,tok)

def test_actual_nonempty_collector_and_registered_service_config(tmp_path):
 import collect,owner,protocol as p,service_wrapper,study as s
 row=next(x for x in p.plan() if x['anchor']=='opaque');context=p.contexts()[row['context_index']];body=s.read(ROOT/'REQUESTS.json')[row['id']];prompt=s.read(ROOT/'PROMPT_IDS.json')[row['id']];content=s.serialize([{'key':key,'label':record['gold_label']} for key,record in zip(p.anchor_values(context,'opaque'),context['records'],strict=True)]);tok=s.tokenizer();tokens=tok.encode(content,add_special_tokens=False)+[tok.eos_token_id];raw={'model':body['model'],'prompt_token_ids':prompt,'choices':[{'index':0,'message':{'role':'assistant','content':content,'tool_calls':None},'finish_reason':'stop','token_ids':tokens,'logprobs':{'content':[{'token':'x','logprob':-1.,'bytes':None,'top_logprobs':[]} for _ in tokens]}}],'usage':{'prompt_tokens':len(prompt),'completion_tokens':len(tokens),'total_tokens':len(prompt)+len(tokens)}}
 endpoint=tmp_path/'endpoint.json';s.write(endpoint,{'host':'fixture','port':1,'api_key_env':'STRICT_RLM_CALIBRATION_API_KEY','model_alias':s.MODEL['alias'],'base_model':s.MODEL,'adapter':None,'max_model_len':s.MAX_MODEL_LEN,'vllm_version':'0.28.0'});original=s.read
 def read(path):return [row] if Path(path)==ROOT/'PLAN.json' else original(path)
 def handler(request):assert json.loads(request.content)==body;return httpx.Response(200,json=raw)
 with patch.object(s,'verify',return_value={'identity':'cpu'}),patch.object(s,'read',side_effect=read),patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'fixture'}):status=asyncio.run(collect.run(endpoint,tmp_path/'rollout',time.time()+60,httpx.MockTransport(handler)))
 assert status['available']==1;assert original(tmp_path/'rollout/calls'/row['id']/'RESULT.json')['score']['contract_valid']
 observed={}
 class Loader:
  def create_module(self,spec):return None
  def exec_module(self,module):module.PRIME_ENV=Path('/fixture/prime');module._port_free=lambda port:True;module._environment=lambda:{'PATH':'/usr/bin','LD_LIBRARY_PATH':''};module._server_environment=lambda environment,replica:dict(environment);module._wait_endpoint_model=lambda endpoint,process,alias,timeout:observed.update(alias=alias)
 prior_spec=util.spec_from_file_location
 def spec(name,path):return machinery.ModuleSpec(name,Loader()) if name=='base_service_environment' else prior_spec(name,path)
 def spawn(command,**kwargs):observed['command']=command;return type('Process',(),{'pid':424242})()
 stage=tmp_path/'owned-service';stage.mkdir();s.write(stage/'BINDING.json',owner.binding())
 with patch.object(util,'spec_from_file_location',spec),patch.object(subprocess,'Popen',spawn),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'fixture','STRICT_RLM_CALIBRATION_API_KEY':'fixture'}),patch.object(sys,'argv',[str(ROOT/'service_wrapper.py'),'--binding',str(stage/'BINDING.json'),'--run-dir',str(stage/'service')]):service_wrapper.main()
 inference=s.read(stage/'service/inference.json');assert observed['alias']==s.MODEL['alias'] and inference['vllm']['model']==str(s.MODEL_PATH) and inference['vllm']['served_model_name']==[s.MODEL['alias']] and inference['vllm']['max_model_len']==s.MAX_MODEL_LEN
