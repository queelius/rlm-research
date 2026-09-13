import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import collect
import study


def test_bijection_changes_only_public_identifier_strings():
    original = [row for row in study.read(study.train.ROOT / "EVAL_TASKS.json")["tasks"]
                if row["split"] == "train"]
    reverse = study.read(study.ROOT / "ID_MAPPING_PUBLIC.json")["reverse"]
    for old, new in zip(original, study.tasks(), strict=True):
        restored = new["prompt"]
        for renamed, source in reverse.items():
            restored = restored.replace(renamed, source)
        assert restored == old["prompt"]
        assert new["seed"] == old["seed"] and new["root_id"] == old["root_id"]
        assert new["request"] == study.train.width.request_body(new["prompt"], new["seed"], 384)
        assert study._rename(study.base.child({"split": "train", "root_id": old["root_id"],
                                             "repeat": old["repeat"]})) == study.child(
                                                 {"split": "train", "root_id": old["root_id"],
                                                  "repeat": old["repeat"]})


def test_actual_inherited_collector_call_uses_renamed_prompt_and_native_body(tmp_path):
    call = study.calls()[0]
    body = study.request_for(call)
    ids = study.tokenizer().encode('{"eligible_ids":[]}', add_special_tokens=False) + [151645]
    observed = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            size = int(self.headers["content-length"])
            observed["body"] = json.loads(self.rfile.read(size))
            response = {"model": body["model"], "request_id": "renamed-cpu-fixture",
                "choices": [{"token_ids": ids, "finish_reason": "stop",
                    "logprobs": {"content": [{"token": f"token_id:{item}", "logprob": -0.2}
                                               for item in ids]}}],
                "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids),
                          "total_tokens": len(body["token_ids"]) + len(ids)}}
            raw = json.dumps(response, separators=(",", ":")).encode()
            self.send_response(200); self.send_header("content-length", str(len(raw))); self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    old = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "fixture"
    try:
        for name in ("calls", "native", "prompts", "starts"):
            (tmp_path / name).mkdir()
        collector = collect.inherited.Collector(
            f"http://127.0.0.1:{server.server_port}/inference/v1/generate", tmp_path, study.now()+30)
        record = collector.call(call, study.prompt(call), child=study.child(call))
    finally:
        server.shutdown(); thread.join(timeout=5)
        if old is None: os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY", None)
        else: os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = old
    assert observed["body"] == body
    assert record["transport_valid"] and record["request_id"] == "renamed-cpu-fixture"
    assert set(json.loads(record["text"])) == {"eligible_ids"}
