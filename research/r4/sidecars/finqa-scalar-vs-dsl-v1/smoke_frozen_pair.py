"""Additive post-seal actual frozen-prefix HTTP proof; synthetic replies, no GPU."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import collect
import metrics
import study

output=study.ROOT / "cpu-frozen-pair-001"
assert not output.exists()
plan=study.read(study.INPUTS)
calls=plan["calls"][:2]
assert calls[0]["context_index"]==calls[1]["context_index"]==0
audit={row["call_id"]:row for row in study.read(study.ROOT / "TOKEN_AUDIT.json")["calls"]}
seen=[]
texts=['{"answer":0}','{"program":[["add",0,0]]}']

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers["content-length"])))
        ids=study.tokenizer().encode(texts[len(seen)],add_special_tokens=False)+[151645]
        seen.append(body)
        response={"model":study.MODEL_ALIAS,"request_id":f"actual-prefix-fixture-{len(seen)}",
                  "choices":[{"token_ids":ids,"finish_reason":"stop","logprobs":{"content":[{"token":f"token_id:{t}","logprob":-.25} for t in ids]}}],
                  "usage":{"prompt_tokens":len(body["token_ids"]),"completion_tokens":len(ids),"total_tokens":len(body["token_ids"])+len(ids)}}
        data=json.dumps(response).encode()
        self.send_response(200);self.send_header("content-length",str(len(data)));self.end_headers();self.wfile.write(data)
    def log_message(self,*_args):pass

old_key=os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
os.environ["STRICT_RLM_CALIBRATION_API_KEY"]="fixture-only"
server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
runner=collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate",output,study.now()+60)
try:
    for index,call in enumerate(calls):
        cid=study.call_id(call)
        record=runner.call(call,plan["prompts"][cid])
        assert record["transport_valid"] and record["text"]==texts[index]
        assert seen[index]==audit[cid]["request"]==study.read(record["request_path"])
        assert study.read(record["prompt_path"])=={"messages":[{"role":"user","content":plan["prompts"][cid]}]}
        assert record["response_sha256"]==study.digest(study.read(record["response_path"]))
finally:
    server.shutdown();thread.join(timeout=5)
    if old_key is None:os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY",None)
    else:os.environ["STRICT_RLM_CALIBRATION_API_KEY"]=old_key
result=metrics.summarize(output,False)
assert result["complete"] is False and result["paired_known"]==1
assert all(arm["available"]==1 and arm["unknown"]==15 and arm["invalid_known"]==0 for arm in result["arms"].values())
assert result["physical_cost"]["physical_started"]==2
study.write_x(output / "METRIC_SMOKE.json",result)
receipt={"schema":"finqa-frozen-actual-pair-HTTP-smoke-v1","passed":True,"GPU_calls":0,"synthetic_replies":True,
         "native_actual_frozen_requests":2,"frozen_context_id":calls[0]["example_id"],"paired_seed":calls[0]["seed"],
         "retained_unknown_slots":30,"unknown_pairs_not_losses":True,"ready_sha256":study.sha(study.READY_RUN),
         "source_pins":[{"path":str(path),"sha256":study.sha(path)} for path in [Path(__file__),study.READY_RUN,study.INPUTS,study.HOST,study.ROOT / "TOKEN_AUDIT.json"]],
         "artifact_pins":[{"path":str(path),"sha256":study.sha(path)} for path in sorted(output.rglob("*.json"))]}
study.write_x(output / "RECEIPT.json",receipt)
print(json.dumps({"receipt":str(output / "RECEIPT.json"),"sha256":study.sha(output / "RECEIPT.json"),"passed":True}))
