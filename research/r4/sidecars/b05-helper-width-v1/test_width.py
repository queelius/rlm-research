"""Actual frozen partitions and native HTTP collector; no GPU/model calls."""
from pathlib import Path
import importlib
import json

def modules():
    assert (Path(__file__).parent/'study.py').exists(), 'width runner absent'
    return tuple(importlib.import_module(n) for n in ('study','interface','collect','metrics','owner'))

def test_union_never_eligibility_repairs_or_converts_unknown_to_empty():
    s,i,c,m,o=modules();root=s.active_roots()[0];calls=[x for x in s.calls() if x['root_id']==root['root_id'] and x['helpers']==4 and x['alternative']==0]
    records={}
    for x in calls:
        part=s.child(x);ids=sorted(r['implementation_id'] for r in part['stage']['tables']['implementations'])
        grade=i.grade(json.dumps({'eligible_ids':ids}),part)
        records[s.call_id(x)]={**x,'transport_valid':True,'child_grade':grade,'physical_started':True,'usage':{}}
    union=m.stage_group(calls,records);target=set(s.gold()[root['root_id']])
    assert union['strict_claim_valid'] and len(union['ids'])==6
    assert set(union['ids'])>target and union['false_positive']>0
    missing=dict(records);missing.pop(s.call_id(calls[0]))
    assert not m.stage_group(calls,missing)['available'] and m.stage_group(calls,missing)['ids'] is None
    invalid=dict(records);key=s.call_id(calls[0]);invalid[key]={**records[key],'child_grade':{'status':'invalid_claim','parsed':None}}
    assert m.stage_group(calls,invalid)['available'] and not m.stage_group(calls,invalid)['strict_claim_valid']

def test_actual14_native_calls_scopes_budgets_and_owner_aliases(tmp_path,monkeypatch):
    s,i,c,m,o=modules()
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    root=s.active_roots()[0];plan=[x for x in s.calls() if x['root_id']==root['root_id']];seen=[]
    tokens=s.tokenizer().encode('{"eligible_ids":[]}',add_special_tokens=False)+[151645]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['content-length'])));seen.append(body)
            response={'model':s.MODEL_ALIAS,'request_id':f'fixture-{len(seen)}',
                'choices':[{'token_ids':tokens,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':-.25} for v in tokens]}}],
                'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(tokens),'total_tokens':len(body['token_ids'])+len(tokens)}}
            raw=json.dumps(response).encode();self.send_response(200);self.send_header('content-length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','fixture-only')
    runner=c.Collector(f'http://127.0.0.1:{server.server_port}/inference/v1/generate',tmp_path,s.now()+60)
    try:runner.root(root)
    finally:server.shutdown();thread.join(timeout=5);server.server_close()
    assert len(seen)==runner.physical==14
    for call,body in zip(plan,seen,strict=True):
        assert body==s.request_body(s.prompt(call),call['seed'],384//call['helpers'])
        row=s.read(tmp_path/'calls'/f'{s.call_id(call)}.json')
        assert row['transport_valid'] and row['child_grade']['status']=='valid_claim'
    actual=o.implementation();assert actual.study is s and actual.collect is c and actual.metrics is m
    assert c.inherited.study is s and not getattr(c.Collector,'b05_contract_clarification_v3',False)
