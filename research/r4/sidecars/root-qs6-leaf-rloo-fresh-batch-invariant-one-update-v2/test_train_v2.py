import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import torch


ROOT = Path(__file__).resolve().parent


def load_train():
    spec = importlib.util.spec_from_file_location("fresh48_one_update_v2", ROOT / "train.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_actual_seed_initialization_uses_uint32_only_for_numpy():
    train = load_train()
    with pytest.raises(ValueError, match="Seed must be between"):
        np.random.seed(train.MASTER_SEED)
    observed = train.initialize_rng(np, torch)
    assert observed == {
        "master": 202609121401,
        "python": 202609121401,
        "numpy_legacy": 745658489,
        "torch": 202609121401,
        "torch_cuda_all": 202609121401,
    }
    assert torch.initial_seed() == train.MASTER_SEED


def test_v1_failure_is_preserved_and_v2_output_is_fresh():
    train = load_train()
    failure = json.loads((train.V1 / "outputs/attempt-001/FAILURE.json").read_text())
    assert failure["optimizer_steps"] == 0
    assert failure["error_type"] == "ValueError"
    assert "2**32" in failure["error"]
    assert not (train.ROOT / "outputs/attempt-001").exists()
    assert train.source_sha256() == train.V1_TRAIN_SHA


def test_wrapper_changes_only_numpy_seed_and_records_seed_receipt(monkeypatch, tmp_path):
    train = load_train()
    source = train.load_v1()
    seen = {}

    def fake_run(output, cap_seconds):
        seen["root"] = source.ROOT
        seen["numpy_seed"] = np.random.seed
        np.random.seed(train.MASTER_SEED)
        Path(output).mkdir(parents=True)
        source.write_x(Path(output) / "RESULT.json", {"status": "UPDATED", "optimizer_steps": 1})
        return {"status": "UPDATED", "optimizer_steps": 1}

    monkeypatch.setattr(source, "run", fake_run)
    result = train.run(tmp_path / "attempt", 900, source=source)
    assert result["status"] == "UPDATED"
    assert seen["root"] == train.ROOT
    receipt = json.loads((tmp_path / "attempt/RNG_SEEDS_ACTUAL.json").read_text())
    assert receipt["numpy_legacy_seed"] == train.NUMPY_SEED
    assert receipt["master_seed_unchanged"] is True
    assert receipt["v1_failure_preserved"] is True
