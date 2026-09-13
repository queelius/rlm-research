"""Candidate-local G4 credit bindings over one fixed native vector batch."""

import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent; STORE = ROOT.parents[1]
FLAT = ROOT.parent / "b05-flat-selection-rl-v1"
spec = importlib.util.spec_from_file_location("vector_local_flat_study", FLAT / "study.py")
flat = importlib.util.module_from_spec(spec); spec.loader.exec_module(flat)
for name in ("sha", "read", "digest", "write_x", "bytes_x", "load", "aliases"):
    globals()[name] = getattr(flat, name)
SHARED = ROOT.parent / "b05-vector-credit-shared-v1"
ROLLOUT = ROOT.parent / "b05-varied-vector-rollouts-v1"
BASE = flat.BASE; NATIVE = flat.NATIVE; PYTHON = flat.PYTHON
CONFIG_SOURCE = flat.CONFIG_SOURCE; PRIOR = flat.PRIOR
INPUTS = SHARED / "TRAIN_INPUTS.json"; READY = ROOT / "READY.json"
OUTPUT = ROOT / "outputs/attempt-001"
INIT_SEED = SEED = 202609480001; NP_SEED = SEED % (2**32)
LEARNING_RATE = 1e-4; DENOMINATOR = 64; TOKEN_TIS_CAP = 2.0
SCIENCE_SECONDS = 900; OWNER_SECONDS = 1000; EXTERNAL_SECONDS = 1100
CREDIT_MODE = "local"
REWARD_DESCRIPTION = "per-candidate binary correctness; candidate-specific G4 RLOO"
ALIAS = "Qwen3-4B-Instruct-2507-b05-vector-credit-local-step1"
positions_and_targets = flat.positions_and_targets


def validate_inputs(data):
    rows = data["episodes"]
    assert data["denominator"] == 64 and data["G"] == 4 and len(rows) == 64
    assert len({row["group_id"] for row in rows}) == 16 and len({row["episode_id"] for row in rows}) == 64
    for path, expected in data["source_pins"].items(): assert sha(path) == expected, path
    for row in rows:
        group = [item for item in rows if item["group_id"] == row["group_id"]]
        assert len(group) == 4 and sorted(item["repeat"] for item in group) == [0, 1, 2, 3]
        assert len(row["root_turns"]) == 1; turn = row["root_turns"][0]; positions_and_targets(turn)
        assert len(turn["input_ids"]) <= 8192 and len(turn["action_ids"]) <= 384
        assert len(row["credit_coefficients"]) == len(turn["action_ids"])
        assert all(len(coeff) == row["candidate_count"] for coeff in row["credit_coefficients"])
        assert len(row["local_advantages"]) == len(row["joint_advantages"]) == row["candidate_count"]
        assert len(row["actual_loss_mask"]) == len(turn["input_ids"])
        assert row["actual_loss_mask"] == [0] * len(turn["prompt_ids"]) + row["bool_union_mask"]
        for token in row["credit_receipt"]["cross_decision_token_indices"]:
            assert not any(row["credit_coefficients"][token])
        if not row["semantic_valid"]:
            assert row["raw_candidate_correctness"] is None
            assert not any(any(coeff) for coeff in row["credit_coefficients"])
            assert row["effective_candidate_rewards"] == [0] * row["candidate_count"]
    for group_id in {row["group_id"] for row in rows}:
        group = [row for row in rows if row["group_id"] == group_id]
        for mode in ("local", "joint"):
            for candidate in range(group[0]["candidate_count"]):
                assert math.isclose(sum(row[mode + "_advantages"][candidate] for row in group),
                                    0.0, abs_tol=1e-12)
    assert any(any(value != 0 for value in row[CREDIT_MODE + "_advantages"]) for row in rows)
    return rows


def verify():
    ready = read(READY); assert ready["identity"] == digest({k: v for k, v in ready.items() if k != "identity"})
    for path, expected in ready["closure_sha256"].items(): assert sha(path) == expected, path
    validate_inputs(read(INPUTS)); return ready

