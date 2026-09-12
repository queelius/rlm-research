"""Fixed AG data, policy, environment and sealed-source interfaces."""

import contextlib
import copy
import functools
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
FROZEN = SIDE / "helper-agnews-data-vs-mechanics-v1/inputs"
EVAL = SIDE / "helper-agnews-heldout-eval-v1"
V1 = SIDE / "root-qs6-leaf-rloo-onebatch-v1"
QUAL = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-qualification-v1"
QUAL2 = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-qualification-v2"
FAST = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-v1"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)
CAP, OUTER_CAP = 1100, 1200
PHASE_CAPS = {"native": 650, "masks": 60, "hf": 350, "cleanup_reserve": 40}
SEED = 202609122300
HOST_GOLD = ROOT / "inputs/HOST_GOLD.json"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


@contextlib.contextmanager
def aliases(mapping):
    previous = {name: sys.modules.get(name) for name in mapping}
    sys.modules.update(mapping)
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def load(name, path, bindings=None):
    with aliases(bindings or {}):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


old = load("ag_native_frozen_study", QUAL / "study.py")
BASE_MODEL = old.BASE_MODEL
CHILD_START = old.CHILD_START
CHILD_ALIAS = old.CHILD_ALIAS
CHILD_SHA = old.CHILD_SHA
SOURCE_BINDING = old.SOURCE_BINDING
SERVICE_WRAPPER = old.SERVICE_WRAPPER
V1_ROOT = QUAL
TOKENIZER_FILES = [
    BASE_MODEL / name for name in ("tokenizer.json", "tokenizer_config.json", "config.json")
]
feedback_study = old.feedback_study
binding = old.binding


def schedule():
    rows = read(ROOT / "inputs/REQUESTS.json")
    for row in rows:
        # JSON canonical storage sorts maps; restore the original schema property order.
        row["body"]["sampling_params"]["structured_outputs"]["json"] = json.loads(
            row["schema_ordered_json"]
        )
    if len(rows) != 128 or len({row["coordinate_id"] for row in rows}) != 128:
        raise ValueError("fixed128 native coordinates differ")
    return rows


@functools.lru_cache(maxsize=1)
def numeric_modules():
    leaf = load("ag_native_exact_math", V1 / "leaf_math.py")
    prepare = load("ag_native_exact_masks", V1 / "prepare.py", {"leaf_math": leaf})
    train = load("ag_native_exact_scores", V1 / "train.py", {"leaf_math": leaf, "prepare": prepare})
    fast = load("ag_native_exact_objective", FAST / "train.py")
    return types.SimpleNamespace(leaf=leaf, prepare=prepare, train=train, fast=fast)


def plan():
    return {
        "schema": "agnews-native-hf-one-update-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "output": str(ATTEMPT),
        "command": [str(NATIVE), str(ROOT / "owner.py"), "run", "--outer-seconds", str(CAP)],
        "owner_cap_seconds": CAP,
        "external_cap_seconds": OUTER_CAP,
        "phase_caps_seconds": PHASE_CAPS,
        "inventory": {
            "native_calls": 128,
            "groups": 32,
            "actions_per_group": 4,
            "records_per_request": 4,
            "unique_training_records": 128,
            "record_decisions": 512,
            "optimizer_steps": 1,
        },
        "policy": {
            "temperature": 0.5,
            "native_concurrency": 4,
            "batch_invariant": True,
            "reward": "fraction_correct_over4",
            "reward_scale": 4,
            "loss": "raw detached full-sequence IS weighted count RLOO score gradient",
            "denominator": 128,
            "lr": 1e-5,
            "weight_decay": 0,
            "clip": 1,
            "ess_min": 102.4,
            "max_normalized_weight": 0.1,
            "token_replay_tolerance": 1e-5,
            "sequence_replay_tolerance": 1e-4,
        },
        "seeds": {
            "native_first": 202609122100,
            "native_last": 202609122227,
            "hf": SEED,
            "numpy_legacy": SEED % (2**32),
        },
        "schedule_sha256": digest(schedule()),
        "launch_authority": "MAIN only under shared GPU lock",
    }


def verify():
    ready = read(ROOT / "READY.json")
    if (
        digest({key: value for key, value in ready.items() if key != "identity"})
        != ready["identity"]
    ):
        raise ValueError("READY identity differs")
    for key, value in plan().items():
        if ready.get(key) != value:
            raise ValueError("READY plan differs: " + key)
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("source closure changed: " + path)
    return ready


def child_binding(checkpoint, state_sha):
    value = copy.deepcopy(read(SOURCE_BINDING))
    source_child = copy.deepcopy(value["models"][CHILD_ALIAS])
    value["models"][CHILD_ALIAS] = {
        "path": str(checkpoint),
        "adapter_sha256": sha(checkpoint / "adapter_model.safetensors"),
        "config_sha256": sha(checkpoint / "adapter_config.json"),
    }
    value["child_only_update"] = {
        "experiment": ROOT.name,
        "step": 1,
        "state_sha256": state_sha,
        "source_child": source_child,
        "root_unchanged": True,
        "qualified_native_hf_importance_corrected": True,
        "qualification_sha256": sha(ATTEMPT / "PRESTEP_QUALIFICATION.json"),
    }
    return value
