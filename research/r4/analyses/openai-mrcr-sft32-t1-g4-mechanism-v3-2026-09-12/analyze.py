"""Independent one-shot raw audit for T1 attempt-003."""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-procedural-sft32-onpolicy-t1-v1"
PRIOR = STORE / "analyses/openai-mrcr-sft32-t1-g4-mechanism-2026-09-12/analyze.py"
SOURCE_CORE = STORE / "analyses/openai-mrcr-sft32-g4-mechanism-2026-09-12/analyze.py"
READY = SIDE / "READY_V3.json"
READY_SHA = "d6eac589f4e045acd82a4025b14cfec1ba5c82908f98eee482d41e5c97d85c90"


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def read(path: Path):
    return json.loads(Path(path).read_text())


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


prior = load("mrcr_t1_v1_analysis_for_v3", PRIOR)
core = prior.core
core.ROOT = ROOT
core.STORE = STORE
core.SIDE = SIDE
core.PINS = {}


@functools.lru_cache(maxsize=1)
def bindings():
    previous_path = list(sys.path)
    names = ("study", "study_v2", "study_v3", "checkpoint", "collect")
    previous = {name: sys.modules.get(name) for name in names}
    try:
        sys.path.insert(0, str(SIDE))
        module = load("mrcr_t1_v3_analysis_entry", SIDE / "collect_v3.py")
    finally:
        sys.path[:] = previous_path
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    collector = module.source.source.source
    expected = STORE / "sidecars/openai-mrcr-procedural-sft32-onpolicy-screen-v1/collect.py"
    if Path(collector.__file__).resolve() != expected:
        raise ValueError("unexpected hook-bearing scientific collector")
    if module.source.source.source.source.model_context is not module.model_context:
        raise ValueError("actual inner executable does not use repaired model_context")
    if collector.role_hooks is not module.role_hooks:
        raise ValueError("actual collector does not use T1 role hook")
    return collector


core.bindings = bindings


def verify_source():
    source = read(ROOT / "SOURCE.json")
    ready = read(READY)
    if sha(READY) != READY_SHA or source["ready_sha256"] != READY_SHA:
        raise ValueError("T1 V3 READY changed")
    if ready["identity"] != source["identity"] or ready["identity"] != digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("T1 V3 identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if sha(Path(raw)) != expected:
            raise ValueError("T1 V3 closure changed: " + raw)
    collector = bindings()
    schedule = collector.study.schedule("train")
    if len(schedule) != 32 or {row["temperature"] for row in schedule} != {1.0}:
        raise ValueError("not the fixed T1 schedule")
    if [row["seed"] for row in schedule] != list(range(202609200000, 202609200032)):
        raise ValueError("requested seeds changed")
    return source


def build():
    source = verify_source()
    value = core.build()
    if value["status"] == "PENDING":
        return value
    value["schema"] = "openai-mrcr-sft32-t1-g4-mechanism-audit-v3"
    value["repair_condition"] = {
        "attempt": 3,
        "ready_sha256": READY_SHA,
        "role_hook_temperature": 1.0,
        "failed_attempts_not_scored": [1, 2],
    }
    value["temperature_treatment"] = {
        "source_temperature": 0.5,
        "treatment_temperature": 1.0,
        "same_requested_seed_integers": True,
        "not_a_new_seed_replication": True,
        "source_t05_raw_exact": 28,
        "source_t05_mixed_groups": 0,
    }
    for group in value["groups"]:
        for sample in group["samples"]:
            for turn in sample["turns"]:
                if turn["sampling"].get("temperature") != 1.0:
                    raise ValueError("physical native request did not retain temperature 1.0")
    value["source_adapter"] = source
    value["analysis_core_path"] = str(SOURCE_CORE)
    value["analysis_core_sha256"] = sha(SOURCE_CORE)
    return value


def markdown(value):
    if value["status"] == "PENDING":
        return "# T1 attempt-003 audit\n\nOwner terminal is absent; partial outputs were not scored.\n"
    vectors = [group["binary_rewards"] for group in value["groups"]]
    return f"""---
schema: openai-mrcr-sft32-t1-g4-mechanism-report-v3
status: {value['status']}
---

# Checkpoint32 temperature-1.0 grouped rollout

Attempt-003 recorded {value['recorded']}/32 trajectories; {value['available']} were scientifically
available and {value['raw_exact_available']} were raw-exact. The fixed G4 reward vectors are
`{vectors}` and {value['mixed_groups']} complete groups are mixed. Attempts 001 and 002 are excluded
because their requests failed before the native endpoint.

The paired T0.5 screen used the same records and requested seed integers and returned 28/32 with
zero mixed groups. This remains a temperature treatment, not an independent seed replication.
Decision status: `{value['decision_proposal_not_training_admission']}`. No optimizer is authorized.
"""


def write_x(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        if isinstance(value, str):
            stream.write(value)
        else:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "check"))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outcome")
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only analyzer requires CUDA_VISIBLE_DEVICES empty")
    if args.command == "verify":
        source = verify_source()
        print(json.dumps({"identity": source["identity"], "ready_sha256": READY_SHA}, sort_keys=True))
    else:
        value = build()
        if value["status"] == "PENDING":
            print(json.dumps(value, sort_keys=True))
            raise SystemExit(2)
        value["created_epoch"] = time.time()
        write_x(args.output_dir / "RESULTS.json", value)
        write_x(args.output_dir / "REPORT.md", markdown(value))
        print(json.dumps({key: value[key] for key in ("status", "raw_exact_available", "complete_groups", "mixed_groups", "decision_proposal_not_training_admission")}, sort_keys=True))
