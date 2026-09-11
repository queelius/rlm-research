import asyncio,json,os,time
from pathlib import Path
from unittest.mock import patch
import httpx
import collect,owner,protocol as p,scoring,study as s

def test_protocol_is_balanced_disjoint_and_explicit():
 rows=p.plan();assert len(rows)==192;assert len({x['id'] for x in rows})==192
 assert {(x['relation'],x['cell']) for x in rows}==set(__import__('itertools').product(p.RELATIONS,p.CELLS))
 for context in p.contexts():
  assert not set(p.tags(context,'A'))&set(p.tags(context,'B'))
 for row in rows:
  text=p.request(p.contexts()[row['context_index']],row)['messages'][1]['content']
  assert 'Output position i always labels displayed input object i' in text

def test_scoring_and_primary_contrast_use_intended_positions():
 rows=[]
 for coordinate in p.plan():
  context=p.contexts()[coordinate['context_index']];labels=[x['gold_label'] for x in context['records']]
  if coordinate['cell'] in ('AB','BA'):labels[16:]=[p.LABELS[(p.LABELS.index(x)+1)%3] for x in labels[16:]]
  message={'content':json.dumps([{'answer_tag':tag,'label':label} for tag,label in zip(p.tags(context,coordinate['output_set']),labels,strict=True)])}
  rows.append({'coordinate':coordinate,'score':scoring.score(message,context,coordinate['arm']),'physical_attempt':False,'usage_observed':None})
 summary=collect.summarize(rows);assert summary['primary']['effect_pp']==100.0
 assert all(x['effect_pp']==100.0 for x in summary['primary']['relation_effects'].values())

def test_actual_nonempty_collector_entry_via_fake_transport(tmp_path):
 row=p.plan()[0];context=p.contexts()[row['context_index']];body=s.read(s.ROOT/'REQUESTS.json')[row['id']];prompts=s.read(s.ROOT/'PROMPT_IDS.json');content=s.serialize([{'answer_tag':tag,'label':record['gold_label']} for tag,record in zip(p.tags(context,row['output_set']),context['records'],strict=True)]);tokenizer=s.tokenizer();completion=tokenizer.encode(content,add_special_tokens=False)+[151645]
 raw={'model':body['model'],'prompt_token_ids':prompts[row['id']],'choices':[{'index':0,'message':{'role':'assistant','content':content,'tool_calls':None},'finish_reason':'stop','token_ids':completion,'logprobs':{'content':[{'token':'x','logprob':-1.0,'bytes':None,'top_logprobs':[]} for _ in completion]}}],'usage':{'prompt_tokens':len(prompts[row['id']]),'completion_tokens':len(completion),'total_tokens':len(prompts[row['id']])+len(completion),'prompt_tokens_details':{'cached_tokens':0}}}
 def handler(request):assert json.loads(request.content)==body;return httpx.Response(200,json=raw)
 endpoint=tmp_path/'endpoint.json';s.write(endpoint,{'host':'fixture','port':1,'api_key_env':'STRICT_RLM_CALIBRATION_API_KEY','model':s.MODEL});original=s.read
 def read(path):return [row] if Path(path)==s.ROOT/'PLAN.json' else original(path)
 with patch.object(s,'verify',return_value={'identity':'cpu'}),patch.object(s,'read',side_effect=read),patch.object(s.service,'validate_descriptor',return_value=None),patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'fixture'}):status=asyncio.run(collect.run(endpoint,tmp_path/'rollout',time.time()+60,httpx.MockTransport(handler)))
 saved=original(tmp_path/'rollout/calls'/row['id']/'RESULT.json');assert status['available']==1 and saved['native_verified'] and saved['score']['strict_correct']==48

def test_owner_exact_namespace_and_registered_service():
 stage=s.ATTEMPT/'owned-service';argv=owner.collector_argv(stage,s.ATTEMPT,123.0);assert owner.validate_argv(argv)['deadline']==123.0
 assert owner.binding()['checkpoint']==s.MODEL and owner.suite().SERVE==s.ROOT/'service_wrapper.py'
