"""Protect literal booleans, exact length, public-order mapping and actual native binding."""
from pathlib import Path
import json
import pytest


def test_vector_requires_literal_bools_exact_length_and_public_order():
    assert (Path(__file__).parent/'interface.py').exists(),'decision vector parser not implemented'
    import interface
    order=['z','a','m']
    value=interface.parse('{"eligible":[true,false,true]}','vector',order)
    assert value['ids']==['z','m'] and value['strict_valid']
    assert interface.parse('{"eligible":[true,false,true]}','vector',['a','z','m'])['ids']==['a','m']
    assert interface.parse('{"eligible_ids":["m","z"]}','list',order)['ids']==['m','z']
    assert not interface.parse('{"eligible_ids":["z","m"]}','list',order)['strict_valid']
    for text in ('{"eligible":[1,false,true]}','{"eligible":[0,1,true]}','{"eligible":["true",false,true]}','{"eligible":[null,false,true]}',
                 '{"eligible":[true,false]}','{"eligible":[true,false,true,false]}','{"eligible":[true,false,true],"x":0}',
                 '{"eligible":[true,false,true],"eligible":[false,false,false]}','```json\n{"eligible":[true,false,true]}\n```'):
        with pytest.raises((ValueError,AssertionError)):interface.parse(text,'vector',order)
    for text in ('{"eligible_ids":["z","z"]}','{"eligible_ids":["unknown"]}'):
        with pytest.raises((ValueError,AssertionError)):interface.parse(text,'list',order)


def test_actual_http_pair_binding_and_invalid_has_no_partial_credit(tmp_path,monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    import collect
    import metrics
    import owner
    import study as s
    plan=s.read(s.INPUTS);calls=plan['calls'][:4];task=plan['tasks'][0];order=task['public_order'];seen=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['content-length'])));call=calls[len(seen)];seen.append(body)
            if call['arm']=='list':value={'eligible_ids':[order[2],order[0]] if call['repeat']==0 else []}
            else:value={'eligible':[(i in (0,2)) for i in range(len(order))] if call['repeat']==0 else ['true']+[False]*(len(order)-1)}
            ids=s.tokenizer().encode(json.dumps(value),add_special_tokens=False)+[151645]
            response={'model':s.MODEL_ALIAS,'request_id':f'vector-fixture-{len(seen)}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.1} for t in ids]}}],
                      'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)}}
            payload=json.dumps(response).encode();self.send_response(200);self.send_header('content-length',str(len(payload)));self.end_headers();self.wfile.write(payload)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','fixture-only')
    runner=collect.Collector(f'http://127.0.0.1:{server.server_port}/inference/v1/generate',tmp_path,s.now()+60)
    try:
        for index,call in enumerate(calls):
            key=s.call_id(call);record=runner.call(call,plan['prompts'][key])
            assert record['transport_valid'] and seen[index]==plan['requests'][key]==s.read(record['request_path'])
            assert record['response_sha256']==s.digest(s.read(record['response_path']))
            assert 'child_grade' not in record and 'source_grade' not in record
    finally:server.shutdown();thread.join(timeout=5)
    assert seen[0]['sampling_params']==seen[1]['sampling_params'] and seen[2]['sampling_params']==seen[3]['sampling_params']
    result=metrics.summarize(tmp_path,False);assert result['available']==4 and result['unknown']==44 and not result['complete']
    bad=next(r for r in result['rows'] if r['arm']=='vector' and r['root_id']==task['root_id'] and r['repeat']==1)
    assert bad['available'] and not bad['semantic_valid'] and bad['ids'] is None and bad['balanced_accuracy'] is None and not bad['exact']
    actual=owner.implementation();assert actual.study is s and actual.collect is collect and actual.metrics is metrics and collect.inherited.study is s
    for t in plan['tasks']:
        assert t['list_prompt'].split('Return exactly one JSON object',1)[0]==t['vector_prompt'].split('Return exactly one JSON object',1)[0]
        assert t['public_order']==[r['implementation_id'] for r in t['normalized_public_view']['stage']['effective_candidates']]
