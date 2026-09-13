"""Focused actual native collector seam; no model or GPU."""
from pathlib import Path
import importlib
import json

def test_actual_both_aliases_full_schedule_and_raw_HTTP(tmp_path,monkeypatch):
    assert (Path(__file__).parent/'study.py').exists(), 'new eval study not implemented'
    s=importlib.import_module('study');c=importlib.import_module('collect');m=importlib.import_module('metrics')
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    plan=s.calls();assert len(plan)==72 and len({s.call_id(x) for x in plan})==72
    assert all(sum(x['split']==split and x['arm']==arm for x in plan)==18 for split in ('train','held') for arm in ('base','cp1'))
    root=s.active_roots()[0];local=[x for x in plan if x['root_id']==root['root_id']];seen=[]
    tokens=s.tokenizer().encode('{"eligible_ids":[]}',add_special_tokens=False)+[151645]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['content-length'])));seen.append(body)
            response=dict(model=body['model'],request_id=f'fixture-{len(seen)}',choices=[dict(token_ids=tokens,finish_reason='stop',
                logprobs={'content':[dict(token=f'token_id:{v}',logprob=-.25) for v in tokens]})],
                usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(tokens),total_tokens=len(body['token_ids'])+len(tokens)))
            raw=json.dumps(response).encode();self.send_response(200);self.send_header('content-length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','fixture-only')
    runner=c.Collector(f'http://127.0.0.1:{server.server_port}/inference/v1/generate',tmp_path,s.now()+60)
    try:runner.root(root)
    finally:server.shutdown();thread.join(timeout=5);server.server_close()
    assert runner.physical==len(seen)==4
    assert {x['model'] for x in seen}=={str(s.train.BASE),s.train.ALIAS}
    for call,body in zip(local,seen,strict=True):
        assert body==s.request_for(call) and len(body['token_ids'])+384<=8192
        row=s.read(tmp_path/'calls'/f'{s.call_id(call)}.json');assert row['transport_valid']
        assert s.decode_response(body,s.read(row['response_path']))['completion_ids']==tokens
        scored=m.grade(call,row);assert scored['available'] and scored['strict_valid'] and scored['semantic_valid']
    assert not m.grade(local[0],{})['available']
    known=s.task(local[0])['known_ids'];assert len(known)>1
    unsorted={**row,'text':json.dumps({'eligible_ids':list(reversed(sorted(known)))})}
    scored=m.grade(local[0],unsorted);assert not scored['strict_valid'] and scored['semantic_valid']
    result=m.summarize(tmp_path,True);assert not result['complete'] and result['cost']['planned']==72

def test_actual_current_runtime_and_real_adapter_binding():
    s=importlib.import_module('study');suite=s.dependencies()
    assert suite.SERVE==s.RUNTIME/'service_wrapper_v2.py' and suite.life.ALLOCATION_SERVICE==suite.SERVE
    binding=s.binding();assert binding['base_control_adapter'] is None
    assert list(binding['models'])==[s.train.ALIAS]
    model=binding['models'][s.train.ALIAS]
    assert model['config_sha256']==s.sha(Path(model['path'])/'adapter_config.json')
    assert model['adapter_sha256']==s.sha(Path(model['path'])/'adapter_model.safetensors')
