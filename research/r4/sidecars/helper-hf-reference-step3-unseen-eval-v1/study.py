"""Fixed-panel readout of reference T1/LR1e-5 checkpoint 3, with full-run authentication."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE_EVAL = SIDE / "helper-hf-fourstep-unseen-eval-v1"
TRAIN_OUTPUT = SIDE / "helper-hf-onpolicy-fourstep-v1/outputs/attempt-001"
ATTEMPT = ROOT / "outputs/attempt-001"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
CAP = 600


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_x(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text() != rendered: raise ValueError("immutable file differs: " + str(path))
    else:
        with path.open("x") as stream: stream.write(rendered)


def _load():
    spec = importlib.util.spec_from_file_location("reference_step3_source_eval", SOURCE_EVAL / "fourstep_panel_study.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


source = _load()
C32 = source.C32
MODEL = source.MODEL
PANEL = source.PANEL
panel = source.panel
schedule = source.schedule
dependencies = source.dependencies


def _validate_step3_with_final_lineage(receipt, state3, commit3, state4, commit4):
    lineage = receipt.get("lineage", receipt.get("full_lineage", []))
    if [row.get("step") for row in lineage] != [1, 2, 3, 4]:
        raise ValueError("authenticated reference lineage is not four complete steps")
    if (lineage[2].get("state_sha256") != digest_file_state(state3) or
            lineage[2].get("step_commit_sha256") != sha(TRAIN_OUTPUT / "checkpoint-0003/STEP_COMMIT.json")):
        raise ValueError("reference checkpoint3 receipt differs")
    parent_commit = {"path": str(TRAIN_OUTPUT / "checkpoint-0003/STEP_COMMIT.json"),
        "sha256": sha(TRAIN_OUTPUT / "checkpoint-0003/STEP_COMMIT.json")}
    if (state4.get("parent_identity") != sha(TRAIN_OUTPUT / "checkpoint-0003/state.json") or
            state4.get("parent_step_commit") != parent_commit or
            commit4.get("parent_identity") != sha(TRAIN_OUTPUT / "checkpoint-0003/state.json") or
            commit4.get("parent_step_commit") != parent_commit or
            state3.get("step") != 3 or commit3.get("step") != 3):
        raise ValueError("reference final step does not descend from checkpoint3")


def digest_file_state(state):
    # State dictionaries are read only from the exact file; this helper makes fixture testing explicit.
    return hashlib.sha256((json.dumps(state, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()).hexdigest()


def qualify():
    source_ready = read(SOURCE_EVAL / "READY.json")
    if source_ready.get("status") != "CPU_READY_CONDITIONAL_ON_COMPLETED_FOURSTEP_PRIMARY":
        raise ValueError("unexpected source evaluator READY")
    for path, expected in source_ready["closure_sha256"].items():
        if sha(path) != expected: raise ValueError("source evaluator closure changed: " + path)
    if digest(schedule()) != source_ready["schedule_sha256"]:
        raise ValueError("source evaluator schedule changed")
    full = source.qualify_fourstep()
    checkpoint3 = TRAIN_OUTPUT / "checkpoint-0003"; checkpoint4 = TRAIN_OUTPUT / "checkpoint-0004"
    state3 = read(checkpoint3 / "state.json"); commit3 = read(checkpoint3 / "STEP_COMMIT.json")
    state4 = read(checkpoint4 / "state.json"); commit4 = read(checkpoint4 / "STEP_COMMIT.json")
    _validate_step3_with_final_lineage(full, state3, commit3, state4, commit4)
    source_binding = read(source.SOURCE_BINDING)
    binding = source.verify_binding(checkpoint3, state3, source_binding, 3)
    if state3.get("cumulative_optimizer_steps") != 3 or state3.get("optimizer_state_steps") != [3]:
        raise ValueError("reference checkpoint3 optimizer state differs")
    source.verify_optimizer_steps(checkpoint3 / "optimizer.pt", 3)
    return {"eligible": True, "schema": "helper-hf-reference-step3-eligibility-v1",
        "policy": "reference T1/LR1e-5 checkpoint-0003 matched-three-update control",
        "fixed_fourstep_primary": False, "selection": "fixed update count, not evaluation selection",
        "completed_reference_optimizer_steps": 4, "evaluated_checkpoint_step": 3,
        "training_ready_identity": full["training_ready_identity"],
        "training_result_sha256": full["training_result_sha256"], "full_lineage": full["lineage"],
        "final_checkpoint_state_sha256": full["checkpoint_state_sha256"],
        "checkpoint": str(checkpoint3), "checkpoint_state_sha256": sha(checkpoint3 / "state.json"),
        "checkpoint_step_commit_sha256": sha(checkpoint3 / "STEP_COMMIT.json"),
        "binding": binding, "binding_sha256": sha(checkpoint3 / "EVAL_BINDING.json")}


def binding():
    receipt = qualify()
    if ATTEMPT.exists(): write_x(ATTEMPT / "ELIGIBILITY.json", receipt)
    return receipt["binding"]


def verify(require_training=True):
    ready = read(ROOT / "READY.json")
    if ready.get("status") != "CPU_READY_REFERENCE_MATCHED_THREE_UPDATE_CONTROL":
        raise ValueError("unexpected READY status")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready.get("identity"):
        raise ValueError("READY identity differs")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected: raise ValueError("eval closure changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]: raise ValueError("fixed256 schedule changed")
    if require_training: qualify()
    return ready
