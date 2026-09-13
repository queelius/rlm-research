"""Catch bool coercion, silently false missing scalars, and native binding/cap mistakes."""
from pathlib import Path
import json
import pytest


def test_scalar_requires_literal_bool_and_full_union_keeps_missing_unknown():
    assert (Path(__file__).parent/'interface.py').exists(), 'singleton interface is not implemented'
    import interface
    assert interface.parse_scalar('{"eligible":true}') is True
    assert interface.parse_scalar('{"eligible":false}') is False
    for text in ('{"eligible":1}', '{"eligible":0}', '{"eligible":"true"}', '{"eligible":null}',
                 '{"eligible":[true]}', '{"eligible":true,"extra":0}', '{"eligible":true,"eligible":false}', 'true'):
        with pytest.raises((ValueError,AssertionError)): interface.parse_scalar(text)
    records={0:{'transport_valid':True,'text':'{"eligible":true}'},1:{'transport_valid':True,'text':'{"eligible":false}'}}
    result=interface.singleton_union(['z','a','m'],records)
    assert not result['available'] and not result['semantic_valid'] and result['ids'] is None
    assert result['unknown_candidates']==[2] and result['invalid_candidates']==[]
    records[2]={'transport_valid':True,'text':'{"eligible":"true"}'}
    result=interface.singleton_union(['z','a','m'],records)
    assert result['available'] and not result['semantic_valid'] and result['ids'] is None
    assert result['unknown_candidates']==[] and result['invalid_candidates']==[2]
    records[2]={'transport_valid':True,'text':'{"eligible":true}'}
    result=interface.singleton_union(['z','a','m'],records)
    assert result['available'] and result['semantic_valid'] and result['ids']==['z','m']


def test_actual_http_scalar_caps_projection_and_partial_stage_accounting(tmp_path,monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    import collect
    import metrics
    import owner
    import study as s
    import interface
    plan=s.read(s.INPUTS);task=plan['tasks'][0];order=task['public_order']
    calls=[c for c in plan['calls'] if c['root_id']==task['root_id'] and c['repeat']==0]
    seen=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['content-length'])));call=calls[len(seen)];seen.append(body)
            if call['arm']=='list': value={'eligible_ids':[order[2],order[0]]}
            elif call['arm']=='vector': value={'eligible':[i in (0,2) for i in range(len(order))]}
            else: value={'eligible':call['candidate_index'] in (0,2)}
            ids=s.tokenizer().encode(json.dumps(value),add_special_tokens=False)+[151645]
            response={'model':s.MODEL_ALIAS,'request_id':f'singleton-fixture-{len(seen)}','choices':[{'token_ids':ids,'finish_reason':'stop',
                'logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.1} for t in ids]}}],
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
            assert seen[index]['sampling_params']['max_tokens']==(16 if call['arm']=='singleton' else 384)
            assert seen[index]['sampling_params']['seed']==202609430000+(1000+call['candidate_index'] if call['arm']=='singleton' else 0)
            assert 'source_grade' not in record and 'child_grade' not in record
    finally:server.shutdown();thread.join(timeout=5)
    result=metrics.summarize(tmp_path,False)
    assert result['planned']==176 and result['available']==8 and result['unknown']==168 and not result['complete']
    assert len(result['rows'])==36 and all(result['arms'][a]['planned']==12 for a in ('list','vector','singleton'))
    rows=[r for r in result['rows'] if r['root_id']==task['root_id'] and r['repeat']==0]
    assert len(rows)==3 and all(r['ids']==[order[2],order[0]] or r['ids']==[order[0],order[2]] for r in rows)
    assert all(r['semantic_valid'] for r in rows) and rows[0]['tp']+rows[0]['fn']==len(s.read(s.HOST)['rows'][0]['gold_ids'])
    actual=owner.implementation();assert actual.study is s and actual.collect is collect and actual.metrics is metrics and collect.inherited.study is s
    for task in plan['tasks']:
        for index,prompt in enumerate(task['singleton_prompts']):
            projected=interface.normalized_public(prompt)
            assert projected['stage']['policy']==task['normalized_public_view']['stage']['policy']
            assert projected['stage']['effective_candidates']==[task['normalized_public_view']['stage']['effective_candidates'][index]]
    assert sum(t['width'] for t in plan['tasks'])==76
