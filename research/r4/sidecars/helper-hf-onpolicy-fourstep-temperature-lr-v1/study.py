"""Identity and verification for two approved four-update helper-policy arms."""

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
CAP = 4200
OUTER_CAP = 4400
ARMS = {
    "t2_lr1e5": {
        "name": "t2_lr1e5",
        "question": "Does temperature2 create more useful within-group feedback diversity?",
        "temperature": 2.0,
        "learning_rate": 1e-5,
        "root": ROOT / "arms/t2-lr1e5",
    },
    "t1_lr1e4": {
        "name": "t1_lr1e4",
        "question": "Does a tenfold learning rate make the existing local signal effective?",
        "temperature": 1.0,
        "learning_rate": 1e-4,
        "root": ROOT / "arms/t1-lr1e4",
    },
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


def plan(arm_name):
    arm = ARMS[arm_name]
    output = arm["root"] / "outputs/attempt-001"
    return {
        "schema": "helper-hf-onpolicy-fourstep-arm-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "arm": {
            "name": arm_name,
            "question": arm["question"],
            "temperature": arm["temperature"],
            "learning_rate": arm["learning_rate"],
            "isolated_change_from_reference": (
                "temperature" if arm_name == "t2_lr1e5" else "learning_rate"
            ),
        },
        "command": [
            str(TRAIN_PYTHON),
            str(ROOT / "train_arm.py"),
            "--arm",
            arm_name,
            "--output",
            str(output),
            "--cap-seconds",
            str(CAP),
        ],
        "output": str(output),
        "owner_cap_seconds": CAP,
        "external_timeout_seconds": OUTER_CAP,
        "launch_authority": "MAIN only under shared GPU flock",
        "start": "original c32; never the completed four-step reference",
        "inventory": {
            "updates": 4,
            "groups_per_update": 32,
            "actions_per_group": 4,
            "fresh_actions_per_update": 128,
            "total_fresh_actions": 512,
            "training_records": 32,
            "evaluation_records_in_training": 0,
        },
        "seeds": {
            "global": 202609120700,
            "sampler": 202609120701,
            "permutation_base_plus_step": 202609120800,
        },
        "fixed_objective": {
            "rloo": "within B4; sequence sum; mean over all128",
            "replay_token_tolerance": 1e-5,
            "replay_sequence_tolerance": 1e-4,
            "first4_full_support_tolerance": 1e-5,
            "weight_decay": 0,
            "gradient_clip_norm": 1.0,
            "fresh_collection_before_each_update": True,
            "carried_adam_within_arm_only": True,
        },
        "metrics": {
            "live_constrained_entropy": "from already-computed sampling logq",
            "live_and_nonforced_position_counts": True,
            "mixed_reward_groups": True,
            "sampled_sequence_logprob_sums": True,
            "poststep_extra_forward_sweep": False,
            "subsequent_collection_match_analysis": "posthoc diagnostic with selection caveat",
        },
        "checkpoint_policy": {
            "save_each_step": True,
            "primary_step": 4,
            "selection_by_eval": False,
            "automatic_resume": False,
        },
        "evaluation": {
            "fixed_panel_records": 256,
            "inner_cap_seconds": 600,
            "external_timeout_seconds": 700,
            "adaptive_reuse_not_pristine_generalization": True,
        },
    }


def verify(arm_name):
    arm = ARMS[arm_name]
    ready = read(arm["root"] / "READY.json")
    for key, expected in plan(arm_name).items():
        if ready.get(key) != expected:
            raise ValueError("arm READY plan changed: " + key)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready.get(
        "identity"
    ):
        raise ValueError("arm READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if sha(raw) != expected:
            raise ValueError("sealed arm source changed: " + raw)
    return ready
