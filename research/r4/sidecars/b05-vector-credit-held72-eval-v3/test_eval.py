"""Actual three-alias HTTP transport plus complete 72-row partial summary."""
import json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import collect,metrics,study
def test_actual_three_alias_http_and_72row_summary(tmp_path,monkeypatch):
    study.verify();calls=study.calls();root=study.active_roots()[0];selected=[c for c in calls if c["root_id"]==root["root_id"] and c["repeat"]==0]
    assert len(selected)==3 and {c["arm"] for c in selected}==set(study.ARMS)
    for name in ("calls","starts","native","prompts","roots"):(tmp_path/name).mkdir()
    order=study.task(selected[0])["public_order"];tokens=study.tokenizer().encode(json.dumps({"eligible":[False]*len(order)}),add_special_tokens=False)+[151645];seen=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers["content-length"])));seen.append(body)
            response={"model":body["model"],"request_id":f"held-v3-{len(seen)}","choices":[{"token_ids":tokens,"finish_reason":"stop","logprobs":{"content":[{"token":f"token_id:{token}","logprob":-.1} for token in tokens]}}],"usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(tokens),"total_tokens":len(body["token_ids"])+len(tokens)}}
            raw=json.dumps(response).encode();self.send_response(200);self.send_header("content-length",str(len(raw)));self.end_headers();self.wfile.write(raw)
        def log_message(self,*_args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY","fixture")
    runner=collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate",tmp_path,study.now()+60)
    try:
        for call in selected:
            row=runner.call(call,study.prompt(call));assert row["transport_valid"]
            scored=metrics.grade(call,row,order,study.gold()[call["root_id"]]);assert scored["available"] and scored["semantic_valid"] and scored["arm"]==call["arm"]
    finally:server.shutdown();thread.join(timeout=5);server.server_close()
    assert {body["model"] for body in seen}=={str(study.BASE),study.local_alias(),study.joint_alias()}
    result=metrics.summarize(tmp_path,False);assert result["planned"]==72 and result["available"]==3 and result["unknown"]==69 and not result["complete"]
    assert all(result["arms"][arm]["available"]==1 for arm in study.ARMS)
