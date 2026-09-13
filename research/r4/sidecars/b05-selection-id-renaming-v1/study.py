"""Frozen train-stage ID-renaming readout over base and fixed cp1."""

import copy
import functools
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_EVAL = ROOT.parent / "b05-flat-selection-rl-eval-v1"
spec = importlib.util.spec_from_file_location("b05_id_rename_eval_source", SOURCE_EVAL / "study.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
for name in ("sha", "read", "digest", "write_x", "bytes_x", "load", "aliases"):
    globals()[name] = getattr(base, name)
train = base.train
source = base.source
SOURCE = base.SOURCE
RUNTIME = base.RUNTIME
NATIVE = base.NATIVE
now = base.now
tokenizer = base.tokenizer
READY = ROOT / "READY.json"
ATTEMPT = ROOT / "outputs/attempt-001"
MAX_PHYSICAL = 36
CONCURRENCY = 4
SCIENCE_SECONDS = 600
OWNER_SECONDS = 700
EXTERNAL_SECONDS = 800


@functools.lru_cache(None)
def tasks():
    return read(ROOT / "RENAMED_TASKS.json")["tasks"]


@functools.lru_cache(None)
def mapping():
    return read(ROOT / "ID_MAPPING_PUBLIC.json")["forward"]


def task(call):
    return next(row for row in tasks()
                if (row["root_id"], row["repeat"]) == (call["root_id"], call["repeat"]))


@functools.lru_cache(None)
def active_roots():
    return [dict(root_id=row["root_id"], split="train", width=row["width"])
            for row in tasks() if row["repeat"] == 0]


@functools.lru_cache(None)
def calls():
    result = []
    for index, root in enumerate(active_roots()):
        for repeat in range(2):
            arms = ("base", "cp1") if (index + repeat) % 2 == 0 else ("cp1", "base")
            for arm in arms:
                row = next(item for item in tasks()
                           if item["root_id"] == root["root_id"] and item["repeat"] == repeat)
                result.append(dict(**root, repeat=repeat, arm=arm, kind="child",
                                   seed=row["seed"], max_tokens=384))
    return result


def call_id(call):
    return f"train-{call['root_id']}-r{call['repeat']}-{call['arm']}"


def prompt(call):
    return task(call)["prompt"]


def request_for(call):
    value = copy.deepcopy(task(call)["request"])
    value["model"] = str(train.BASE) if call["arm"] == "base" else train.ALIAS
    return value


decode_response = base.decode_response
b05 = base.b05


def _rename(value):
    if isinstance(value, str):
        return mapping().get(value, value)
    if isinstance(value, list):
        return [_rename(item) for item in value]
    if isinstance(value, dict):
        return {key: _rename(item) for key, item in value.items()}
    return value


def child(call):
    return _rename(base.child(call))


def gold():
    return {(row["split"], row["root_id"]): set(row["gold_ids"])
            for row in read(ROOT / "HOST_GOLD.json")["rows"]}


binding = base.binding
dependencies = base.dependencies


def verify():
    ready = read(READY)
    assert ready["identity"] == digest({key: value for key, value in ready.items() if key != "identity"})
    for path, expected in ready["closure_sha256"].items():
        assert sha(path) == expected, path
    assert len(active_roots()) == 9 and len(calls()) == 36
    assert len({call_id(call) for call in calls()}) == 36
    assert read(ROOT / "INPUTS.json")["calls"] == [
        dict(call=call, request=request_for(call), prompt=prompt(call)) for call in calls()
    ]
    assert binding() == read(ROOT / "BINDING.json")
    for call in calls():
        assert len(request_for(call)["token_ids"]) + 384 <= 8192
    dependencies()
    return ready

