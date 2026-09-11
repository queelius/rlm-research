import asyncio,itertools,json,os,time
from pathlib import Path
from unittest.mock import patch
import httpx
import collect,owner,protocol as p,scoring,study as s

def response(context,row,labels):
 return {'content':s.serialize([{'answer_tag':tag,'label':label} for tag,label in zip(p.tags(context,row['output_set']),labels,strict=True)])}

def test_active_reference_fields_and_balanced_cell_dispatch():
 rows=p.plan();assert len(rows)==192 and len({x['id'] for x in rows})==192
 assert {(x['relation'],x['cell']) for x in rows}==set(itertools.product(p.RELATIONS,p.CELLS))
 for position in range(4):
  assert {cell:sum(x['pair_position']==position and x['cell']==cell for x in rows) for cell in p.CELLS}=={cell:12 for cell in p.CELLS}
 for row in rows:
  context=p.contexts()[row['context_index']];body=p.request(context,row);records=json.loads(body['messages'][1]['content'].split('Input records:\n',1)[1]);assert [x['requested_tag'] for x in records]==p.requested_tags(context);assert [x['id'] for x in records]==p.visible_ids(context,row['relation']);assert all('input_tag' in x for x in records);assert 'requested_tag is an opaque output address' in body['messages'][1]['content']

def test_named_reference_diagnostic_has_correct_direction():
 context=p.contexts()[0];wrong=next(x for x in p.plan() if x['context_index']==0 and x['relation']=='wrong');visible={identifier:record['gold_label'] for identifier,record in zip(p.visible_ids(context,'wrong'),context['records'],strict=True)};named=[visible[x] for x in p.requested_tags(context)];w=scoring.score(response(context,wrong,named),context,wrong);assert w['named_record_correct']==48 and w['strict_correct']<48
 aligned=next(x for x in p.plan() if x['context_index']==0 and x['relation']=='aligned');gold=[x['gold_label'] for x in context['records']];a=scoring.score(response(context,aligned,gold),context,aligned);assert a['named_record_correct']==48 and a['strict_correct']==48
 alien=next(x for x in p.plan() if x['context_index']==0 and x['relation']=='alien');assert scoring.score(response(context,alien,gold),context,alien)['named_record_correct'] is None

def test_actual_nonempty_collector_entry_via_fake_transport(tmp_path):
 row=p.plan()[0];context=p.contexts()[row['context_index']];body=s.read(s.ROOT/'REQUESTS.json')[row['id']];prompts=s.read(s.ROOT/'PROMPT_IDS.json');content=response(context,row,[x['gold_label'] for x in context['records']])['content'];tokenizer=s.tokenizer();completion=tokenizer.encode(content,add_special_tokens=False)+[151645];raw={'model':body['model'],'prompt_token_ids':prompts[row['id']],'choices':[{'index':0,'message':{'role':'assistant','content':content,'tool_calls':None},'finish_reason':'stop','token_ids':completion,'logprobs':{'content':[{'token':'x','logprob':-1.0,'bytes':None,'top_logprobs':[]} for _ in completion]}}],'usage':{'prompt_tokens':len(prompts[row['id']]),'completion_tokens':len(completion),'total_tokens':len(prompts[row['id']])+len(completion),'prompt_tokens_details':{'cached_tokens':0}}}
 def handler(request):assert json.loads(request.content)==body;return httpx.Response(200,json=raw)
 endpoint=tmp_path/'endpoint.json';s.write(endpoint,{'host':'fixture','port':1,'api_key_env':'STRICT_RLM_CALIBRATION_API_KEY','model':s.MODEL});original=s.read
 def read(path):return [row] if Path(path)==s.ROOT/'PLAN.json' else original(path)
 with patch.object(s,'verify',return_value={'identity':'cpu'}),patch.object(s,'read',side_effect=read),patch.object(s.service,'validate_descriptor',return_value=None),patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'fixture'}):status=asyncio.run(collect.run(endpoint,tmp_path/'rollout',time.time()+60,httpx.MockTransport(handler)))
 saved=original(tmp_path/'rollout/calls'/row['id']/'RESULT.json');assert status['available']==1 and saved['native_verified'] and saved['score']['strict_correct']==48

def test_owner_targets_v2_only():
 argv=owner.collector_argv(s.ATTEMPT/'owned-service',s.ATTEMPT,123.0);assert owner.validate_argv(argv)['output']==s.ATTEMPT/'rollout';assert argv[1]==str(s.ROOT/'collect.py')
