"""Focused safe-DSL/scale tests and actual HTTP request/response seam."""
from pathlib import Path
import json


def test_safe_dsl_matches_explicit_arithmetic_and_preserves_percent_scale():
    assert (Path(__file__).parent / "science.py").exists(), "restricted interpreter not implemented"
    import science
    public = {"question": "fixture", "pre_text": ["Values 18.9 and -0.3."], "post_text": [],
              "table": [["label", "a", "b"], ["cost", "$ 10", "20%"]]}
    assert science.evaluate('{"program":[["add",18.9,-0.3]]}', "restricted_dsl", public)["value"] == 18.6
    assert science.evaluate('{"program":[["divide",1,3]]}', "restricted_dsl", public)["value"] == .33333
    assert science.evaluate('{"answer":"93.5%"}', "direct_scalar", public)["value"] == .935
    assert science.evaluate('{"answer":93.5}', "direct_scalar", public)["value"] == 93.5
    assert science.evaluate('{"program":[["table_sum","cost","none"]]}', "restricted_dsl", public)["value"] == 10.2
    for op,want in (("table_max",10.),("table_min",.2),("table_average",5.1)):
        assert science.evaluate(json.dumps({"program":[[op,"cost","none"]]}),"restricted_dsl",public)["value"]==want
    for op,a,b,want in (("subtract",1,3,-2.),("multiply",2,3,6.),("exp",2,3,8.),("greater",3,2,"yes")):
        assert science.evaluate(json.dumps({"program":[[op,a,b]]}),"restricted_dsl",public)["value"]==want
    assert science.evaluate('{"program":[["add",9,8],["divide","#0",2]]}', "restricted_dsl", public)["value"] == 8.5
    for bad in ('{"program":[["divide",1,0]]}', '{"program":[["add","#0",1]]}',
                '{"program":[["__import__","os","none"]]}', '{"program":[["exp",2,100000]]}',
                '{"program":[["table_sum","missing","none"]]}', '{"program":[["add",true,1]]}',
                '{"program":[["add",1,2]],"program":[]}'):
        assert science.evaluate(bad, "restricted_dsl", public)["status"] == "invalid"
    duplicated = {**public, "table": public["table"] + [["cost", "2", "3"]]}
    assert science.evaluate('{"program":[["table_sum","cost","none"]]}', "restricted_dsl", duplicated)["status"] == "invalid"
    too_long = json.dumps({"program": [["add",1,2]]*6})
    assert science.evaluate(too_long,"restricted_dsl",public)["status"] == "invalid"
    invented = science.evaluate('{"program":[["add",987654,1]]}',"restricted_dsl",public)
    assert invented["status"] == "valid" and invented["source_operand_value_presence"] is False


def test_actual_paired_native_http_seam_and_current_owner_binding(tmp_path,monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    import collect
    import metrics
    import owner
    import science
    import study
    public={"question":"What is the sum?","pre_text":["Values 18.9 and -0.3."],"post_text":[],"table":[["label","value"]]}
    calls=[{"kind":arm,"seed":202609290000,"max_tokens":384,"context_index":0,"example_id":"fixture"}
           for arm in ("direct_scalar","restricted_dsl")]
    seen=[]
    answers=['{"answer":18.6}','{"program":[["add",18.9,-0.3]]}']
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers["content-length"])))
            ids=study.tokenizer().encode(answers[len(seen)],add_special_tokens=False)+[151645]
            seen.append(body)
            value={"model":study.MODEL_ALIAS,"request_id":f"fixture-{len(seen)}",
                   "choices":[{"token_ids":ids,"finish_reason":"stop","logprobs":{"content":[{"token":f"token_id:{token}","logprob":-.25} for token in ids]}}],
                   "usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(ids),"total_tokens":len(body["token_ids"])+len(ids)}}
            payload=json.dumps(value).encode()
            self.send_response(200);self.send_header("content-length",str(len(payload)));self.end_headers();self.wfile.write(payload)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY","fixture-only")
    runner=collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate",tmp_path,study.now()+60)
    try:
        for index,call in enumerate(calls):
            prompt=science.prompt(public,call["kind"])
            record=runner.call(call,prompt)
            assert record["transport_valid"] and record["text"]==answers[index]
            assert "source_grade" not in record and "child_grade" not in record
            saved=study.read(record["prompt_path"])
            request=study.read(record["request_path"])
            assert saved=={"messages":[{"role":"user","content":prompt}]}
            assert request==seen[index]==study.request_body(prompt,202609290000,384)
            assert record["response_sha256"]==study.digest(study.read(record["response_path"]))
            assert science.evaluate(record["text"],call["kind"],public)["value"]==18.6
    finally:
        server.shutdown();thread.join(timeout=5)
    assert runner.physical==2 and seen[0]["sampling_params"]==seen[1]["sampling_params"]
    actual=owner.implementation()
    assert actual.collect is collect and actual.metrics is metrics and actual.study is study
