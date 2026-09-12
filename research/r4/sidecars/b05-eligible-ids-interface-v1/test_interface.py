"""Focused ID selection/public-field lookup and actual native boundary regressions."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "b05-recombination-feasibility-v1"


def test_interface_never_filters_claimed_ineligible_ids_or_repairs_schema():
    assert (ROOT / "interface.py").exists(), "new ID-only interface is not implemented"
    import interface
    import study
    root = study.active_roots()[0]
    child = root["safe_children"][1]
    receipt = interface.reference().child_reference_receipt(child)
    ineligible = next(row for row in receipt["derivations"] if not row["eligible"])
    identifier = ineligible["implementation_id"]
    text = json.dumps({"eligible_ids": [identifier]})
    claim = interface.grade(text, child)
    assert claim["status"] == "valid_claim"
    looked_up = interface.lookup(claim["parsed"]["eligible_ids"], child)
    assert looked_up == {"row_count": 1, "rows": [ineligible["effective_row"]]}
    assert interface.grade(json.dumps({"eligible_ids": [identifier, identifier]}), child)["status"] == "invalid_claim"
    assert interface.grade('{"eligible_ids":["not_a_local_ID"]}', child)["status"] == "invalid_claim"
    assert interface.grade('{"eligible_ids":[],"row_count":0}', child)["status"] == "invalid_claim"
    assert interface.grade('{"eligible_ids":[],"eligible_ids":[]}', child)["status"] == "invalid_claim"
    original = root["child_prompts"][1]
    rendered = interface.render(original)
    public_prefix = original.split("Return the complete eligible relation as exactly one JSON object", 1)[0]
    assert rendered.startswith(public_prefix)
    suffix = rendered[len(public_prefix):]
    assert "eligible_ids" in suffix and "row_count" not in suffix and "features" not in suffix
    assert identifier not in suffix


def test_actual_six_child_http_calls_keep_seeds_prefixes_invalids_and_owner_binding(tmp_path, monkeypatch):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading
    import collect
    import interface
    import owner
    import study
    root = study.active_roots()[0]
    calls = [call for call in study.calls() if call["root_id"] == root["root_id"]]
    seen = []
    tokenized = [study.tokenizer().encode(json.dumps({"eligible_ids": []}), add_special_tokens=False)+[151645],
                 study.tokenizer().encode('{"eligible_ids":["invalid_local_id"]}', add_special_tokens=False)+[151645]]

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            seen.append(body)
            ids = tokenized[len(seen) == 2]
            response = {"model": study.MODEL_ALIAS, "request_id": f"fixture-{len(seen)}",
                        "choices": [{"token_ids": ids, "finish_reason": "stop", "logprobs": {"content": [
                            {"token": f"token_id:{token}", "logprob": -.25} for token in ids]}}],
                        "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids),
                                  "total_tokens": len(body["token_ids"])+len(ids)}}
            payload = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("content-length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "fixture-only")
    runner = collect.Collector(f"http://127.0.0.1:{server.server_port}/inference/v1/generate", tmp_path, study.now()+60)
    try:
        runner.root(root)
    finally:
        server.shutdown()
        thread.join(timeout=5)
    assert len(seen) == runner.physical == 6
    for index, call in enumerate(calls):
        record = study.read(tmp_path / "calls" / (study.call_id(call)+".json"))
        saved = study.read(record["prompt_path"])["messages"][0]["content"]
        original = root["child_prompts"][call["child_index"]]
        assert saved == interface.render(original)
        assert seen[index] == study.request_body(saved, call["seed"], 384)
        assert seen[index]["sampling_params"]["temperature"] == .5
        assert record["child_grade"]["status"] == ("invalid_claim" if index == 1 else "valid_claim")
    actual = owner.implementation()
    assert actual.collect is collect and actual.study is study
    assert not getattr(actual.collect.Collector, "b05_contract_clarification_v3", False)
    assert actual.collect.inherited.study is study
