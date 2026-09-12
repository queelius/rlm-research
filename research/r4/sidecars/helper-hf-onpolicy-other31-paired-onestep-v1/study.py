"""Frozen identity for a single shared collection and two paired one-step branches."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
REFERENCE = SIDE / "helper-hf-onpolicy-fourstep-v1"
HF_V1 = SIDE / "helper-hf-onpolicy-v1"
HF_V2 = SIDE / "helper-hf-onpolicy-v2"
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
CHILD = SIDE / "trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128"
SOURCE_BINDING = SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)
OUTPUT = ROOT / "outputs/attempt-001"
GLOBAL_SEED = 202609121700
SAMPLER_SEED = 202609121701
PERMUTATION_SEED = 202609121801
CAP = 2700
OUTER_CAP = 2850
STAGE_CAPS = {"collection": 450, "rloo": 700, "other31": 1600}
BASELINES = {
    "rloo": "within-question leave-one-action-out RLOO",
    "other31": "detached leave-current-question-out other31x4 mean",
}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def plan():
    return {
        "schema": "helper-hf-onpolicy-other31-paired-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "question": "Can action-independent negative verifier evidence update all-failure groups?",
        "command": [
            str(TRAIN_PYTHON),
            str(ROOT / "train_pair.py"),
            "--output",
            str(OUTPUT),
            "--cap-seconds",
            str(CAP),
        ],
        "output": str(OUTPUT),
        "owner_cap_seconds": CAP,
        "external_timeout_seconds": OUTER_CAP,
        "stage_caps_seconds": STAGE_CAPS,
        "launch_authority": "MAIN only under shared GPU flock",
        "inventory": {
            "shared_fresh_actions": 128,
            "groups": 32,
            "actions_per_group": 4,
            "branches": ["rloo", "other31"],
            "optimizer_steps_per_branch": 1,
            "evaluation_records_in_training": 0,
        },
        "policy": {
            "start": "original c32 for collection and both branches",
            "temperature": 1.0,
            "learning_rate": 1e-5,
            "loss": "sequence sum; denominator128",
            "attention": "eager",
            "batch": 4,
            "kv_cache": False,
            "mode": "eval/dropoutoff",
        },
        "seeds": {
            "global": GLOBAL_SEED,
            "sampler": SAMPLER_SEED,
            "permutation": PERMUTATION_SEED,
        },
        "baselines": BASELINES,
        "gates": {
            "token_logprob": 1e-5,
            "sequence_logprob": 1e-4,
            "first4_full_support_logprob": 1e-5,
            "all128_required": True,
            "no_importance_weight": True,
        },
        "checkpoint_policy": {
            "one_step_each": True,
            "fresh_adam_each": True,
            "bit_identical_c32_restore": True,
            "partial_branch_not_promoted": True,
        },
        "evaluation": {
            "fixed_panel_records": 256,
            "inner_cap_seconds": 600,
            "external_timeout_seconds": 700,
            "selection_by_eval": False,
        },
    }


def verify():
    ready = read(ROOT / "READY.json")
    for key, expected in plan().items():
        if ready.get(key) != expected:
            raise ValueError("paired READY plan changed: " + key)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready.get(
        "identity"
    ):
        raise ValueError("paired READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if sha(raw) != expected:
            raise ValueError("sealed paired source changed: " + raw)
    return ready
