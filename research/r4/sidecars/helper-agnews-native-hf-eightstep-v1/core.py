"""Frozen per-step schedules, prior-checkpoint authentication and native bindings."""

import ast
import copy
import importlib.util
import inspect
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "helper-agnews-native-hf-onestep-v1"
DATA = SIDE / "helper-agnews-broader-data-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
spec = importlib.util.spec_from_file_location("ag_eight_original_study", SOURCE / "ag_study.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
read, sha, digest, write_x = original.read, original.sha, original.digest, original.write_x


def load_bound(name, path, bindings):
    with original.aliases(bindings):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module


def initial_parent():
    checkpoint = original.CHILD_START
    return {
        "step": 0,
        "checkpoint": str(checkpoint),
        "adapter_sha256": original.CHILD_SHA,
        "config_sha256": sha(checkpoint / "adapter_config.json"),
        "source_c32_adapter_sha256": original.CHILD_SHA,
        "optimizer_steps": 0,
        "step_commit_sha256": None,
    }


def binding_from_parent(parent):
    checkpoint = Path(parent["checkpoint"])
    if sha(checkpoint / "adapter_model.safetensors") != parent["adapter_sha256"]:
        raise ValueError("exact parent adapter hash differs")
    if sha(checkpoint / "adapter_config.json") != parent["config_sha256"]:
        raise ValueError("exact parent adapter config differs")
    value = copy.deepcopy(read(original.SOURCE_BINDING))
    if value["fixed_child"] != original.CHILD_ALIAS:
        raise ValueError("fixed native child alias differs")
    value["models"][original.CHILD_ALIAS] = {
        "path": str(checkpoint),
        "adapter_sha256": parent["adapter_sha256"],
        "config_sha256": parent["config_sha256"],
    }
    value["eightstep_policy_parent"] = copy.deepcopy(parent)
    return value


def verify_commit(step, attempt=ATTEMPT):
    checkpoint = attempt / f"step-{step:03d}/checkpoint-{step:04d}"
    commit = read(checkpoint / "STEP_COMMIT.json")
    if commit["status"] != "UPDATED" or commit["step"] != step or commit["optimizer_steps"] != step:
        raise ValueError("parent is not the complete expected optimizer step")
    ready = read(ROOT / "READY.json")
    if commit["ready_identity"] != ready["identity"]:
        raise ValueError("parent commit belongs to another source closure")
    for path, expected in commit["files_sha256"].items():
        if sha(path) != expected:
            raise ValueError("committed parent artifact changed: " + path)
    state = read(checkpoint / "state.json")
    if (
        state["optimizer_state_steps"] != [step]
        or state["optimizer_steps"] != step
        or state["status"] != "UPDATED"
        or state["source_c32_adapter_sha256"] != original.CHILD_SHA
    ):
        raise ValueError("parent optimizer/c32 lineage differs")
    qualification = read(attempt / f"step-{step:03d}/PRESTEP_QUALIFICATION.json")
    replay = read(attempt / f"step-{step:03d}/GRADIENT_REPLAY_CHECK.json")
    if not qualification["gate_passed"] or not replay["all128_passed"]:
        raise ValueError("parent lacks complete probability qualification")
    output = attempt / f"step-{step:03d}"
    result, terminal = read(output / "RESULT.json"), read(output / "OWNER_TERMINAL.json")
    if (
        result.get("status") != "UPDATED"
        or result.get("optimizer_steps") != step
        or result.get("step_commit_sha256") != sha(checkpoint / "STEP_COMMIT.json")
        or not terminal.get("complete")
        or not terminal.get("released_before_hf")
        or terminal.get("errors")
        or terminal.get("result_sha256") != sha(output / "RESULT.json")
        or qualification["optimizer_steps"] != step - 1
        or replay["optimizer_steps"] != step - 1
        or len(qualification["episode_ids"]) != 128
        or len(replay["episodes"]) != 128
        or any(not row["passed"] for row in replay["episodes"])
    ):
        raise ValueError("parent completion/replay/service receipt inconsistent")
    return {
        "step": step,
        "checkpoint": str(checkpoint),
        "adapter_sha256": sha(checkpoint / "adapter_model.safetensors"),
        "config_sha256": sha(checkpoint / "adapter_config.json"),
        "state_sha256": sha(checkpoint / "state.json"),
        "optimizer_sha256": sha(checkpoint / "optimizer.pt"),
        "rng_sha256": sha(checkpoint / "rng_state.pt"),
        "step_commit_sha256": sha(checkpoint / "STEP_COMMIT.json"),
        "source_c32_adapter_sha256": original.CHILD_SHA,
        "optimizer_steps": step,
    }


def parent_for(step, attempt=ATTEMPT):
    if not 1 <= step <= 9:
        raise ValueError("step must be1..9")
    parent = initial_parent()
    for previous in range(1, step):
        current = verify_commit(previous, attempt)
        state = read(Path(current["checkpoint"]) / "state.json")
        if state["parent_policy"] != parent:
            raise ValueError("eight-step chain does not start at exact c32/carry every parent")
        parent = current
    return parent


def verify():
    ready = read(ROOT / "READY.json")
    if (
        digest({key: value for key, value in ready.items() if key != "identity"})
        != ready["identity"]
    ):
        raise ValueError("READY identity differs")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed source/input changed: " + path)
    return ready


def step_view(step, *, parent=None, attempt=ATTEMPT):
    parent = parent_for(step, attempt) if parent is None else parent
    if parent["step"] != step - 1:
        raise ValueError("step parent number differs")
    view = types.SimpleNamespace(
        **{key: value for key, value in vars(original).items() if not key.startswith("__")}
    )
    view.ROOT, view.ATTEMPT = ROOT, attempt / f"step-{step:03d}"
    view.STEP, view.PARENT = step, parent
    view.CHILD_START, view.CHILD_SHA = Path(parent["checkpoint"]), parent["adapter_sha256"]
    view.SEED = 202609125000
    view.HOST_GOLD = ROOT / f"inputs/step-{step:03d}/HOST_GOLD.json"
    view.CAP = read(ROOT / "RUNTIME.json")["step_owner_seconds"]
    view.PHASE_CAPS = read(ROOT / "RUNTIME.json")["phase_caps_seconds"]

    def schedule():
        rows = read(DATA / f"inputs/step-{step:03d}/REQUESTS.json")
        for row in rows:
            row["body"]["sampling_params"]["structured_outputs"]["json"] = json.loads(
                row["schema_ordered_json"]
            )
        if len(rows) != 128 or len({row["coordinate_id"] for row in rows}) != 128:
            raise ValueError("frozen step128 schedule differs")
        return rows

    view.schedule = schedule
    view.binding = lambda: binding_from_parent(parent)
    view.verify = verify
    return view


def native_module(view):
    return load_bound(
        f"ag_eight_native_step_{view.STEP}", SOURCE / "native_collect.py", {"ag_study": view}
    )


def numeric_source(view):
    return load_bound(
        f"ag_eight_numeric_step_{view.STEP}", SOURCE / "train_ag.py", {"ag_study": view}
    )


def patched_function(module, name, substitutions):
    source = inspect.getsource(getattr(module, name))
    for before, after in substitutions:
        if source.count(before) != 1:
            raise ValueError("sealed metadata seam differs: " + before)
        source = source.replace(before, after)
    tree = ast.parse(source)
    exec(compile(tree, str(SOURCE / Path(module.__file__).name), "exec"), module.__dict__)
    return getattr(module, name)


def step_owner(view):
    native = native_module(view)
    return load_bound(
        f"ag_eight_owner_step_{view.STEP}",
        SOURCE / "owner.py",
        {"ag_study": view, "native_collect": native},
    )
