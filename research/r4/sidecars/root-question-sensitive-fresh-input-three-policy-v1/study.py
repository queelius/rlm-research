"""Fresh-input evaluation bindings for fixed24 and two exact SFT6 roots."""
import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ORIGINAL = SIDE / "root-question-sensitive-sft-v1"
RECOVERY = SIDE / "root-question-sensitive-sft-recovery-v1"
NEW = SIDE / "root-question-sensitive-sft-new-corpus-completion-v2"
ATTEMPT = ROOT / "outputs/attempt-001"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
NAMESPACE = ROOT.name

_old_path = list(sys.path)
try:
    sys.path[:0] = [str(ORIGINAL), str(RECOVERY)]
    import qs_study as base
    import qs_binding as fixed_binding
    import postcapture_binding as original_sft_binding
finally:
    sys.path[:] = _old_path
original_sft_binding.OUTPUT = RECOVERY / "outputs/attempt-003"
read, write, sha, digest, load, aliases = base.read, base.write, base.sha, base.digest, base.load, base.aliases
CHILD_SHA = base.CHILD_SHA


def selected_new():
    directory = NEW / "outputs/attempt-001/training"
    result, selected = read(directory / "RESULT.json"), read(directory / "SELECTION.json")
    if (not result["complete"] or result["optimizer_steps"] != 6 or result["selected"] != selected
            or selected["step"] != 6 or not result["fresh_optimizer"]
            or result["child_loaded"] or result["child_updated"]):
        raise ValueError("exact complete new-corpus SFT6 required")
    for name, pin in {"adapter_model.safetensors": selected["adapter_sha256"],
                      "adapter_config.json": selected["config_sha256"],
                      "state.json": selected["state_sha256"]}.items():
        if sha(Path(selected["checkpoint"]) / name) != pin:
            raise ValueError("new-corpus checkpoint changed: " + name)
    return selected


def binding(arm):
    if arm == "fixed24":
        value = fixed_binding.binding("unchanged")
    elif arm == "original_sft6":
        value = original_sft_binding.binding("sft6")
    elif arm == "new_corpus_sft6":
        chosen = selected_new()
        value = original_sft_binding.qualified.qualified.binding("sft6", chosen)
    else:
        raise ValueError("exact three-policy comparison only")
    value["study"] = ROOT.name
    value["campaign_id"] = ROOT.name
    value["question_sensitive"]["arm"] = arm
    value["fresh_input"] = {"arm": arm, "new_root_context_groups": True,
                            "fixed_child": CHILD_SHA}
    if value["models"][value["fixed_child"]]["adapter_sha256"] != CHILD_SHA:
        raise ValueError("fixed c32 child changed")
    return value


def validate(value, descriptor, path):
    if value != binding(value["fresh_input"]["arm"]):
        raise ValueError("actual binding differs")
    joint = base.joint()
    validator = load("fresh_input_descriptor_validator", joint.SOURCE / "binding.py",
                     "865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1",
                     {"study": joint.original})
    validator.validate_descriptor(value, descriptor, sha(path))


def make_task(context, row, gold):
    return base.qnative().make_task(context, row["question"], gold, row["id"])


@functools.lru_cache(maxsize=1)
def stack():
    native = base.qnative().stack().native
    def task(context, prompt, gold, name):
        query = read(ROOT / "inputs/PROMPTS_ACCURATE.json")[name]["plain_query"]
        value = base.qnative().make_task(context, query, gold, name)
        if value.data.prompt != prompt:
            raise ValueError("exact fresh-input native prefix")
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


def runtime():
    return base.runtime()


def verify():
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("frozen closure changed: " + path)
    for arm in ready["policy_order"]:
        binding(arm)
    return ready
