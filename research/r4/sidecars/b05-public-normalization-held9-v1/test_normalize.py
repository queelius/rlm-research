"""Mechanical public joins and native fixed raw/normalized pair, no model."""
from pathlib import Path


def test_applied_deltas_union_minus_all_removals_latest_checks_and_retained_ids():
    assert (Path(__file__).parent/"normalize.py").exists(), "normalizer not implemented"
    import normalize
    a=dict(implementation_id="a",input_format="csv",output_format="json",base_cost=10,base_latency=5,base_capacity=7,base_quality=8,base_features=["a","c"])
    b={**a,"implementation_id":"b","base_cost":999}
    def delta(status,revision,add,remove,cost):
        return dict(implementation_id="a",status=status,revision=revision,feature_add=add,feature_remove=remove,cost_delta=cost,latency_delta=0,capacity_delta=0,quality_delta=0)
    stage=dict(policy={"required_checks":["schema","security"],"max_cost":20,"max_latency":10,"min_capacity":5,"min_quality":3},
               tables={"implementations":[a,b],"changes":[delta("applied",1,"b","a",4),delta("draft",2,"z","c",99),delta("applied",3,"a","b",2)],
                       "checks":[dict(implementation_id="a",check_name="schema",revision=r,passed=v) for r,v in [(1,True),(3,False),(2,True)]]})
    rows=normalize.effective_candidates(stage)
    assert [r["implementation_id"] for r in rows]==["a","b"]
    assert rows[0]["cost"]==16 and rows[0]["features"]==["c"]
    assert rows[0]["latest_required_checks"]=={"schema":{"revision":3,"passed":False},"security":None}
    assert rows[1]["cost"]==999 and rows[1]["latest_required_checks"]["schema"] is None
    assert all(set(r)=={"implementation_id","input_format","output_format","cost","latency","capacity","quality","features","latest_required_checks"} for r in rows)


def test_actual_frozen_raw_normalized_pair_http_and_unordered_metric(tmp_path,monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import json
    import threading
    import collect
    import metrics
    import normalize
    import owner
    import study
    p=study.read(study.INPUTS);calls=p["calls"][:2];seen=[]
    assert {c["arm"] for c in calls}=={"raw","normalized"} and calls[0]["seed"]==calls[1]["seed"]
    task=next(t for t in p["tasks"] if t["root_id"]==calls[0]["root_id"])
    answers=[{"eligible_ids":sorted(task["known_ids"][:2],reverse=True)},{"eligible_ids":[]}]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers["content-length"])));index=len(seen);seen.append(body)
            ids=study.tokenizer().encode(json.dumps(answers[index]),add_special_tokens=False)+[151645]
            value={"model":study.MODEL_ALIAS,"request_id":f"normalizer-fixture-{index}","choices":[{"token_ids":ids,"finish_reason":"stop","logprobs":{"content":[{"token":f"token_id:{t}","logprob":-.1} for t in ids]}}],"usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(ids),"total_tokens":len(body["token_ids"])+len(ids)}}
            raw=json.dumps(value).encode();self.send_response(200);self.send_header("content-length",str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY","fixture-only")
    runner=collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate",tmp_path,study.now()+60)
    try:
        for i,c in enumerate(calls):
            key=study.call_id(c);r=runner.call(c,p["prompts"][key])
            assert r["transport_valid"] and r["response_sha256"]==study.digest(study.read(r["response_path"]))
            assert seen[i]==p["requests"][key]==study.read(r["request_path"])
            assert "child_grade" not in r and "source_grade" not in r
    finally:server.shutdown();thread.join(timeout=5)
    assert seen[0]["sampling_params"]==seen[1]["sampling_params"]
    partial=metrics.summarize(tmp_path,False)
    assert partial["available"]==2 and partial["complete"] is False and partial["unknown"]==34
    first=next(r for r in partial["rows"] if r["call_id"]==study.call_id(calls[0]))
    assert first["semantic_valid"] and not first["strict_valid"]
    module=owner.implementation();assert module.study is study and module.collect is collect and module.metrics is metrics
    assert collect.inherited.study is study
    for t in p["tasks"]:
        original=normalize.public_view(t["raw_prompt"])[0]
        normalized=normalize.normalized_view(original)
        assert [r["implementation_id"] for r in normalized["stage"]["effective_candidates"]]==[r["implementation_id"] for r in original["stage"]["tables"]["implementations"]]
        assert normalized["stage"]["policy"]==original["stage"]["policy"]
