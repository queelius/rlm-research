"""Focused regression for the inherited physical Collector.call seam."""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import collect_v2
import owner_v2
import study_v2 as study


def test_actual_collector_call_uses_clock_native_decode_and_source_grade(tmp_path):
    root = study.roots()[0]
    call = next(
        item
        for item in study.calls()
        if item["root_id"] == root["root_id"] and item["kind"] == "direct"
    )
    prompt = study.contract().clarify(call, root["direct_prompt"])
    expected_body = study.request_body(prompt, call["seed"], call["max_tokens"])
    answer = study.source().canonical_json(study.host_by_root()[root["root_id"]]["exact_root_answer"])
    answer_ids = study.tokenizer().encode(answer, add_special_tokens=False)
    observed = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            observed["path"] = self.path
            observed["authorization"] = self.headers.get("authorization")
            size = int(self.headers["content-length"])
            observed["body"] = json.loads(self.rfile.read(size))
            response = {
                "model": study.MODEL_ALIAS,
                "request_id": "cpu-fixture-provider-id",
                "choices": [
                    {
                        "token_ids": answer_ids,
                        "finish_reason": "stop",
                        "logprobs": {
                            "content": [
                                {"token": f"token_id:{token_id}", "logprob": -0.25}
                                for token_id in answer_ids
                            ]
                        },
                    }
                ],
                "usage": {
                    "prompt_tokens": len(expected_body["token_ids"]),
                    "completion_tokens": len(answer_ids),
                },
            }
            encoded = json.dumps(response, separators=(",", ":")).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    old_key = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "cpu-fixture-only"
    try:
        for name in ("calls", "native", "prompts", "starts"):
            (tmp_path / name).mkdir()
        endpoint = f"http://127.0.0.1:{server.server_port}/inference/v1/generate"
        collector = collect_v2.source.Collector(endpoint, tmp_path, study.now() + 30)
        record = collector.call(call, prompt, root=root["safe_root"])
    finally:
        server.shutdown()
        thread.join(timeout=5)
        if old_key is None:
            os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY", None)
        else:
            os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = old_key

    assert observed["path"] == "/inference/v1/generate"
    assert observed["authorization"] == "Bearer cpu-fixture-only"
    assert observed["body"] == expected_body
    assert record["transport_valid"] is True
    assert record["status"] == "returned_valid"
    assert record["source_grade"]["status"] == "correct"
    assert record["text"] == answer
    assert record["request_id"] == "cpu-fixture-provider-id"
    assert record["started_epoch"] <= record["ended_epoch"]
    saved = study.read(tmp_path / "calls" / f"{study.call_id(call)}.json")
    assert saved == record


def test_owner_and_inherited_collector_are_bound_to_repaired_namespace():
    assert owner_v2.source.study is study
    assert owner_v2.source.collect is collect_v2
    assert collect_v2.source.study is study
    assert callable(collect_v2.source.study.now)
    assert study.ATTEMPT.name == "attempt-002"
