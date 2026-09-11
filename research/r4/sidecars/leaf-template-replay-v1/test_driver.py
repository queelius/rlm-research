"""CPU-only reconstruction and actual HF generate-boundary tests."""

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def d():
    assert (ROOT / "driver.py").exists(), "template replay driver missing"
    loader = importlib.util.spec_from_file_location("template_replay_cpu_test", ROOT / "driver.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def spec(d):
    return d.build_spec()


def test_six_contexts_pair_exact_saved_and_reconstructed_templates(d, spec):
    assert len(spec["rows"]) == 12
    assert (
        spec["adapter_sha256"] == "59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200"
    )
    assert len({g for r in spec["rows"] for g in r["group_ids"]}) == 384
    for a, b in zip(spec["rows"][::2], spec["rows"][1::2], strict=True):
        assert a["context_id"] == b["context_id"]
        assert {a["condition"], b["condition"]} == {"probe", "training"}
        assert a["messages"] == b["messages"] and a["gold"] == b["gold"]
        assert a["prompt_ids"] != b["prompt_ids"] and len(a["prompt_ids"]) == len(b["prompt_ids"])
    assert all(
        r["training_render_exact"]
        and r["probe_render_exact"]
        and r["only_tool_key_serialization_differs"]
        for r in spec["reconstruction"]
    )


def test_outer_identity_rejects_changed_physical_prompt_ids(d, spec):
    changed = deepcopy(spec)
    changed["rows"][0]["prompt_ids"][0] += 1
    with pytest.raises(ValueError, match="identity"):
        d.check_identity(changed)


def test_frozen_evaluator_hits_audited_real_generate_boundary_once(d, spec, tmp_path):
    import torch

    tokenizer = d.mixed.data.load_tokenizer()
    rows = spec["rows"][:2]
    content = json.dumps(["entity"] * 64)
    output_ids = tokenizer.encode(content, add_special_tokens=False) + [tokenizer.eos_token_id]

    class CPUModel:
        device = torch.device("cpu")
        generation_config = SimpleNamespace(eos_token_id=tokenizer.eos_token_id)

        def eval(self):
            return self

        def gradient_checkpointing_disable(self):
            pass

        def generate(self, **kwargs):
            extension = torch.tensor([output_ids, output_ids], dtype=torch.long)
            return torch.cat((kwargs["input_ids"], extension), dim=1)

    wrapped = d.AuditedModel(CPUModel(), rows, tokenizer.pad_token_id, tmp_path, lambda: None)
    d.mixed.evaluate_long(wrapped, tokenizer, rows, tmp_path, spec["identity"], d.CHECKPOINT)
    assert wrapped.calls == 1
    actual = d.read(tmp_path / "GENERATE_INPUT.json")
    assert actual["do_sample"] is False and actual["max_new_tokens"] == 1024
    assert actual["input_ids"][0] != actual["input_ids"][1]
    for row in rows:
        result = d.read(tmp_path / (row["id"] + ".json"))
        assert result["prompt_token_ids"] == row["prompt_ids"]
        assert result["score"]["array_valid"] is True
        assert result["finish_reason"] == "stop"


def test_unavailable_completion_is_null_and_malformed_array_not_semantic64_wrong(d, spec, tmp_path):
    summary = d.summarize(spec, tmp_path)
    assert all(r["strict_reward"] is None for r in summary["coordinates"])
    assert all(c["aligned_records"] == 0 for c in summary["cells"])
    score = d.mixed.old.score('["entity"]', spec["rows"][0]["gold"])
    assert score["array_valid"] is False
    assert score["predictions"] == [None] * 64
