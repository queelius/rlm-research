import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import collect
import owner
import study


def canonical(rows):
    return sorted(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows)


def test_unresolved_view_is_lossless_grouping_without_resolution():
    for task in study.read(study.INPUTS)["tasks"]:
        raw = task["raw_public_view"]; grouped = task["unresolved_public_view"]
        original = raw["stage"]["tables"]; records = grouped["stage"]["candidate_records"]
        assert [row["implementation"] for row in records] == original["implementations"]
        assert canonical([row for item in records for row in item["all_change_rows"]]) == canonical(original["changes"])
        assert canonical([row for item in records for row in item["all_check_rows"]]) == canonical(original["checks"])
        assert "effective_candidates" not in grouped["stage"]
        assert task["unresolved_prompt"] == study.represent.render_unresolved(task["raw_prompt"])
        assert task["resolved_prompt"] == study.normalize.render(task["raw_prompt"])


def test_actual_native_http_path_for_all_three_views(tmp_path):
    calls = []
    first_root = study.read(study.INPUTS)["tasks"][0]["root_id"]
    for arm in ("raw", "unresolved", "resolved"):
        calls.append(next(call for call in study.calls()
                          if call["root_id"] == first_root and call["repeat"] == 0 and call["arm"] == arm))
    bodies = {study.call_id(call): study.read(study.INPUTS)["requests"][study.call_id(call)] for call in calls}
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            seen.append(body); ids = study.tokenizer().encode('{"eligible_ids":[]}', add_special_tokens=False)+[151645]
            response = {"model": study.MODEL_ALIAS, "request_id": f"fixture-{len(seen)}",
                "choices": [{"token_ids": ids, "finish_reason": "stop",
                    "logprobs": {"content": [{"token": f"token_id:{value}", "logprob": -0.2} for value in ids]}}],
                "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids),
                          "total_tokens": len(body["token_ids"])+len(ids)}}
            raw = json.dumps(response, separators=(",", ":")).encode(); self.send_response(200)
            self.send_header("content-length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

        def log_message(self, *_args): pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    old = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"); os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "fixture"
    try:
        for name in ("calls","native","prompts","starts"): (tmp_path/name).mkdir()
        runner = collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate",
                                   tmp_path, study.now()+30)
        for call in calls:
            runner.call(call, study.read(study.INPUTS)["prompts"][study.call_id(call)])
    finally:
        server.shutdown(); thread.join(timeout=5)
        if old is None: os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY", None)
        else: os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = old
    assert seen == [bodies[study.call_id(call)] for call in calls]
    assert owner.implementation().study is study
