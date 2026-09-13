"""Actual frozen paired prefix/HTTP binding; no model or GPU service."""
from pathlib import Path


def test_examples_bind_same_facts_to_requested_representation():
    assert (Path(__file__).parent / "interface.py").exists(), "few-shot interface not implemented"
    import interface
    import study
    original = study.read(study.PARENT / "PUBLIC_INPUTS.json")
    prepared = study.read(study.INPUTS)
    assert original["contexts"] == prepared["contexts"] and original["calls"] == prepared["calls"]
    assert study.read(study.HOST) == study.read(study.PARENT / "HOST_TARGETS.json")
    a,b = interface.examples("direct_scalar"),interface.examples("restricted_dsl")
    assert [{k:v for k,v in r.items() if k!="response"} for r in a] == [{k:v for k,v in r.items() if k!="response"} for r in b]
    for i,want in enumerate((5.,.25)):
        for arm,rows in (("direct_scalar",a),("restricted_dsl",b)):
            import json
            assert study.science.evaluate(json.dumps(rows[i]["response"]),arm,{"table":[],"pre_text":[],"post_text":[]})["value"] == want
    assert b[0]["response"]["program"][1][1] == "#0"
    assert b[0]["response"]["program"][2][1] == "#1"
    for call in prepared["calls"]:
        public = prepared["contexts"][call["context_index"]]["public"]
        prompt = prepared["prompts"][study.call_id(call)]
        assert prompt == interface.prompt(public,call["kind"])
        assert prompt.endswith(interface.public_text(public))
        assert prompt.count("Synthetic demonstrations") == 1
        expected_key = "answer" if call["kind"]=="direct_scalar" else "program"
        assert all(set(row["response"])=={expected_key} for row in interface.examples(call["kind"]))


def test_actual_first_pair_http_and_inherited_entrypoint(tmp_path,monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import json
    import threading
    import collect
    import metrics
    import owner
    import study
    plan=study.read(study.INPUTS); calls=plan["calls"][:2]
    audit={row["call_id"]:row for row in study.read(study.ROOT/"TOKEN_AUDIT.json")["calls"]}
    replies=['{"answer":0}','{"program":[["add",0,0]]}'];seen=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers["content-length"])))
            ids=study.tokenizer().encode(replies[len(seen)],add_special_tokens=False)+[151645]
            seen.append(body)
            value={"model":study.MODEL_ALIAS,"request_id":f"fewshot-fixture-{len(seen)}",
                   "choices":[{"token_ids":ids,"finish_reason":"stop","logprobs":{"content":[{"token":f"token_id:{t}","logprob":-.25} for t in ids]}}],
                   "usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(ids),"total_tokens":len(body["token_ids"])+len(ids)}}
            raw=json.dumps(value).encode();self.send_response(200);self.send_header("content-length",str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY","fixture-only")
    runner=collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate",tmp_path,study.now()+60)
    try:
        for i,call in enumerate(calls):
            key=study.call_id(call);record=runner.call(call,plan["prompts"][key])
            assert record["transport_valid"] and record["text"]==replies[i]
            assert study.read(record["request_path"])==seen[i]==audit[key]["request"]
            assert record["response_sha256"]==study.digest(study.read(record["response_path"]))
            assert study.read(record["prompt_path"])["messages"][0]["content"]==plan["prompts"][key]
    finally:server.shutdown();thread.join(timeout=5)
    assert seen[0]["sampling_params"]==seen[1]["sampling_params"]
    partial=metrics.summarize(tmp_path,False)
    assert partial["paired_known"]==1 and partial["complete"] is False
    assert all(v["available"]==1 and v["unknown"]==15 for v in partial["arms"].values())
    module=owner.implementation()
    assert module.study is study and module.collect is collect and module.metrics is metrics
    assert collect.inherited.inherited.study is study
