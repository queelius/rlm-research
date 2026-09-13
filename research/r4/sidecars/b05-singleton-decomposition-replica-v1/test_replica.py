"""Catch stale six-case/176-call accounting and wrong per-scalar native parent bindings."""
from pathlib import Path
import json


def test_actual_replica_schedule_and_native_http(tmp_path,monkeypatch):
    assert (Path(__file__).parent/'PUBLIC_INPUTS.json').exists(),'fresh12-cell schedule is not implemented'
    import study as s
    import collect
    import metrics
    import owner
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    plan=s.read(s.INPUTS);tasks=plan['tasks'];assert len(tasks)==12 and len(plan['calls'])==328
    assert {(t['width'],t['history_depth'],t['check_revisions']) for t in tasks}=={(w,h,c) for w in (6,12,20) for h in (1,3) for c in (1,3)}
    assert sum(t['width'] for t in tasks)==152
    calls=plan['calls'][:7];assert calls[0]['arm']=='vector' and [c['candidate_index'] for c in calls[1:]]==list(range(6));seen=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['content-length'])));call=calls[len(seen)];seen.append(body)
            value={'eligible':[True,False,True,False,False,False]} if call['arm']=='vector' else {'eligible':call['candidate_index'] in (0,2)}
            ids=s.tokenizer().encode(json.dumps(value),add_special_tokens=False)+[151645]
            reply={'model':s.MODEL_ALIAS,'request_id':f'singleton-replica-fixture-{len(seen)}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.1} for t in ids]}}],
                'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)}}
            raw=json.dumps(reply).encode();self.send_response(200);self.send_header('content-length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','fixture-only')
    runner=collect.Collector(f'http://127.0.0.1:{server.server_port}/inference/v1/generate',tmp_path,s.now()+60)
    try:
        for i,call in enumerate(calls):
            key=s.call_id(call);record=runner.call(call,plan['prompts'][key]);assert record['transport_valid']
            assert seen[i]==plan['requests'][key] and record['response_sha256']==s.digest(s.read(record['response_path']))
            assert seen[i]['sampling_params']['seed']==202609500000+(1000+call['candidate_index'] if call['arm']=='singleton' else 0)
            assert seen[i]['sampling_params']['max_tokens']==(16 if call['arm']=='singleton' else 384)
    finally:server.shutdown();thread.join(timeout=5)
    result=metrics.summarize(tmp_path,False)
    assert result['planned']==328 and result['available']==7 and result['unknown']==321 and not result['complete']
    assert result['context_units']==12 and result['stage_seed_units']==24 and len(result['rows'])==48
    assert set(result['arms'])=={'vector','singleton'} and all(a['planned']==24 for a in result['arms'].values())
    first=[r for r in result['rows'] if r['root_id']==tasks[0]['root_id'] and r['repeat']==0]
    assert len(first)==2 and first[0]['ids']==first[1]['ids'] and all(r['seed']==202609500000 for r in first)
    actual=owner.implementation();assert actual.study is s and actual.collect is collect and actual.metrics is metrics and collect.inherited.study is s
