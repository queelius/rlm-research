"""Protect full-array parsing, token spans and the actual64-call binding."""
from pathlib import Path
import json


def test_native_boolean_spans_preserve_structure_and_invalids():
    assert (Path(__file__).parent/'diagnostics.py').exists(),'rollout diagnostics not implemented'
    import diagnostics as d
    import study as s
    text=' {"eligible": [true, false, true]}\n'
    ids=s.tokenizer().encode(text,add_special_tokens=False)+[151645]
    record={'text':text,'completion_ids':ids}
    spans=d.native_spans(record,['z','a','m'])
    assert spans['qualified'] and len(spans['decisions'])==3
    for decision,want in zip(spans['decisions'],('true','false','true')):
        lo,hi=decision['character_span'];assert text[lo:hi]==want and decision['token_indices']
        assert decision['raw_boolean']==want
    bad={**record,'text':'{"eligible":[true,false]}'}
    assert not d.native_spans(bad,['z','a','m'])['qualified']
    values=[dict(semantic_valid=True,ids=['z','m'],balanced_accuracy=1.,exact=True),dict(semantic_valid=True,ids=['a','m'],balanced_accuracy=.25,exact=False)]
    assert not d.group_contrast(values,['z','a','m'],{'z','m'})['full_G4_valid']
    full=values+[values[0],values[1]];contrast=d.group_contrast(full,['z','a','m'],{'z','m'})
    assert contrast['full_G4_valid'] and contrast['variable_candidate_positions']==[0,1]


def test_actual_http_four_samples_and_frozen_held_boundary(tmp_path,monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    import collect
    import metrics
    import owner
    import study as s
    plan=s.read(s.INPUTS);held=s.read(s.HELD);calls=plan['calls'][:4];seen=[]
    assert len(plan['tasks'])==16 and len(plan['calls'])==64 and len(held['tasks'])==12 and len(held['calls'])==24
    assert {t['width'] for t in plan['tasks']}=={6,12} and sum(t['width']==6 for t in plan['tasks'])==8
    assert all(c['arm']=='vector' for c in plan['calls']) and len({c['seed'] for c in calls})==4
    assert not {t['root_id'] for t in plan['tasks']}&{t['root_id'] for t in held['tasks']}
    assert {t['check_revisions'] for t in held['tasks']}=={1,3}
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['content-length'])));call=calls[len(seen)];seen.append(body)
            bits=[True]*call['width'] if call['repeat']!=3 else [1]*call['width']
            ids=s.tokenizer().encode(json.dumps({'eligible':bits}),add_special_tokens=False)+[151645]
            value={'model':s.MODEL_ALIAS,'request_id':f'varied-fixture-{len(seen)}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.1} for t in ids]}}],
                'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)}}
            payload=json.dumps(value).encode();self.send_response(200);self.send_header('content-length',str(len(payload)));self.end_headers();self.wfile.write(payload)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','fixture-only')
    runner=collect.Collector(f'http://127.0.0.1:{server.server_port}/inference/v1/generate',tmp_path,s.now()+60)
    try:
        for i,call in enumerate(calls):
            key=s.call_id(call);record=runner.call(call,plan['prompts'][key]);assert record['transport_valid']
            assert seen[i]==plan['requests'][key] and record['response_sha256']==s.digest(s.read(record['response_path']))
    finally:server.shutdown();thread.join(timeout=5)
    result=metrics.summarize(tmp_path,False)
    assert result['planned']==64 and result['available']==4 and result['unknown']==60 and not result['complete']
    assert result['summary']['invalid_known']==1 and result['full_valid_G4_groups']==0
    assert len(result['groups'])==16 and sum(r['native_spans'].get('qualified',False) for r in result['rows'])==3
    module=owner.implementation();assert module.study is s and module.collect is collect and module.metrics is metrics and collect.inherited.study is s
