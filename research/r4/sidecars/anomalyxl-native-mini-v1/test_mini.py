"""Two focused fixtures for native/executor semantics and official reward/public data."""

import importlib

import pytest


def test_current_executor_is_credential_scrubbed_and_final_receives_remaining_budget(
    tmp_path, monkeypatch
):
    m = importlib.import_module("mini")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-private-fixture")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "cpu-private-fixture")
    m.write(tmp_path / "context.json", {"series": {"x": [1, 2, 3]}})
    with m.executor(tmp_path) as worker:
        result = m.execute_cell(
            worker,
            "```python\nimport os,json,numpy as np\n"
            'assert "STRICT_RLM_CALIBRATION_API_KEY" not in os.environ\n'
            'assert "AWS_SECRET_ACCESS_KEY" not in os.environ\n'
            'print(int(np.sum(json.load(open("context.json"))["series"]["x"])))\n```',
            5,
        )
        assert result["stdout"].strip() == "6" and result["exception"] is None
        with pytest.raises(Exception, match="fenced"):
            m.execute_cell(worker, "print(6)", 5)
    assert m.output_allowance(0, False) == 512
    assert m.output_allowance(700, True) == 1348
    assert m.output_allowance(1536, True) == 512
    observation, inventory = m.observation({"stdout": "x" * 9000})
    assert len(observation) == 2048 and inventory["truncated"]
    tok = m.tokenizer()
    body = m.body([{"role": "user", "content": "Return only {}."}], 123)
    assert body["sampling_params"]["stop_token_ids"] == [248044, 248046]
    import native_service
    from prime_rl.configs.inference import InferenceConfig

    config = native_service.configuration(tmp_path / "service")
    InferenceConfig.model_validate(config)
    assert config["vllm"]["model"] == str(m.MODEL) and not config["vllm"]["enable_lora"]
    assert "api_key" not in config["vllm"] and config["server"]["host"] == "127.0.0.1"
    ids = tok.encode("{}", add_special_tokens=False)
    raw = {
        "request_id": "fixture",
        "model": str(m.MODEL),
        "choices": [{"token_ids": ids, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids)},
    }
    assert m.decode(body, raw)["text"] == "{}"
    raw["usage"]["completion_tokens"] += 1
    with pytest.raises(ValueError, match="tokens"):
        m.decode(body, raw)
    with pytest.raises(ValueError, match="context"):
        m.body([{"role": "user", "content": "word " * 9000}], 2048)


def test_official_scorer_preserves_extractable_prose_and_metadata_only_inventory():
    m = importlib.import_module("mini")
    gold = 'localize:{"present":true,"start":10,"end":30,"_L":100}'
    result = m.score('Answer: {"present":true,"start":20,"end":30}', gold)
    assert result["primary"] == 0.5 and not result["strict_whole_json"]
    assert m.score("not JSON", gold)["primary"] == 0
    assert m.score('{"present":false}', 'localize:{"present":false,"_L":100}')["primary"] == 1
    panel = m.select_metadata()
    assert len(panel) == len({r["id"] for r in panel}) == 10
    assert len({r["category"] for r in panel}) == 5
    assert all(
        set(r) == {"row_index", "id", "category", "length", "n_channels", "seed"} for r in panel
    )
    assert [r["id"] for r in m.select_metadata()] == [r["id"] for r in panel]
    assert len(m.episode_schedule(panel)) == 20
