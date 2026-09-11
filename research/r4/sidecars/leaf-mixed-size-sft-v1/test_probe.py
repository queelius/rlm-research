import importlib.util
from pathlib import Path


def test_greedy_probe_preserves_six_selected_contexts_and_native_capture():
    path = Path(__file__).with_name("probe.py")
    assert path.exists(), "greedy backend probe missing"
    spec = importlib.util.spec_from_file_location("probe_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.build_requests()
    assert len(result["requests"]) == 6
    assert len({r["context_id"] for r in result["requests"]}) == 6
    for row in result["requests"]:
        body = row["request"]
        assert body["temperature"] == 0 and body["max_tokens"] == 1024
        assert body["return_token_ids"] is True
        assert "structured_outputs" not in body
        assert body["model"].endswith("sft-selected-v1")
        assert len(row["gold"]) == 64
