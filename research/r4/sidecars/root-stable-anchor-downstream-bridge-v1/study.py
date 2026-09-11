"""Pinned study facade over the qualified QS6 service/runtime."""

import contextlib
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ATTEMPT = ROOT / "outputs/attempt-001"
INPUTS = ROOT / "inputs"
SCALE = SIDE / "root-qs-scale-harness-factorial-recovery-v1"
QS = scale.QS if "scale" in globals() else SIDE / "root-question-sensitive-sft-v1"
STABLE = SIDE / "leaf-mnli-stable-anchor-vs-sequence-counting-v1"
ANALYSIS = ROOT.parent.parent / "analyses/leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
ACTIVE_MAPS = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, sort_keys=True, indent=2, allow_nan=False); handle.write("\n")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@contextlib.contextmanager
def aliases(values):
    old = {key: sys.modules.get(key) for key in values}; sys.modules.update(values)
    try: yield
    finally:
        for key, value in old.items():
            if value is None: sys.modules.pop(key, None)
            else: sys.modules[key] = value


def load(name, path, pin, alias=None):
    if sha(path) != pin: raise ValueError("qualified source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with aliases(alias or {}): spec.loader.exec_module(module)
    return module


scale = load("downstream_scale", SCALE / "study.py", "fdba67abe33347a7eec083affd2bb1aa7d4c06039d3d7edd5b18e5c37a68aa82")
QS = scale.QS
stable = load("downstream_stable", STABLE / "study.py", "a11a23ba286745a32a16b9c47e9cbceaa995fffa9bf3a1cbbecf9fa399b13243")
qs_protocol = load("downstream_qs_protocol", SCALE / "protocol.py", "198bc44bf411b2ab2ff71486df4ec4908895391b89e2ee8439e2a937571a2091", {"study": scale})
base = scale.base
qnative = scale.base.base.qnative()
ORIGINAL = scale.ORIGINAL
JOINT = scale.JOINT
LABELS = scale.LABELS
corpus = scale.corpus
def answer(records, gold, row):
    import protocol as local
    return local.reduce_answer({"records": records}, gold, row["question"])


def runtime(): return scale.runtime()
def protocol(): return qs_protocol


def binding():
    value = scale.binding("sft6")
    value["study"] = ROOT.name; value["campaign_id"] = ROOT.name
    value["stable_anchor_downstream_bridge"] = {"leaf_calls": 16, "root_episodes": 64,
        "encodings": ["sequential_numeric", "opaque"], "root_policies": ["supplied", "free"],
        "fixed_child": "c32", "root": "qs6", "no_training": True}
    return value


def validate(value, descriptor, path):
    if value != binding(): raise ValueError("binding changed")
    scale.validate(scale.binding("sft6"), descriptor, path)


def make_task(context, row, gold, predicted):
    import protocol as local
    task = qnative.make_task(context, local.root_prompt(context, row), gold, row["id"])
    setup0, finalize0 = task.setup, task.finalize
    async def setup(trace, env):
        await setup0(trace, env)
        await env.write("classification_map.json", json.dumps(predicted, sort_keys=True).encode())
        helper = ("import json,pathlib\n"
            "def classify_all():\n"
            " p=pathlib.Path('map_api_calls.jsonl'); p.write_text((p.read_text() if p.exists() else '')+'call\\n')\n"
            " return json.load(open('classification_map.json'))\n")
        await env.write("map_api.py", helper.encode())
    async def finalize(trace, env):
        result = await env.run(["python", "-c", "import pathlib; p=pathlib.Path('map_api_calls.jsonl'); print(p.read_text() if p.exists() else '')"], {})
        trace.info["canonical_map_api"] = {"calls": result.stdout.count("call"), "stdout": result.stdout,
            "predicted_map_sha256": digest(predicted)}
        await finalize0(trace, env)
    task.setup, task.finalize = setup, finalize
    task.data = task.data.model_copy(update={"prompt": local.root_prompt(context, row),
        "source_split": "mnli-validation-matched-new-inventory-weighted-metadata"})
    return task


@functools.lru_cache(maxsize=1)
def stack():
    native = qnative.stack().native
    plan = {row["id"]: row for row in read(INPUTS / "ROOT_PLAN.json")}
    public = {row["id"]: row for row in read(INPUTS / "PUBLIC.json")}
    maps = ACTIVE_MAPS
    if maps is None: raise ValueError("leaf maps not acquired before root stack")
    def task(context, prompt, gold, name):
        row = plan[name]; value = make_task(public[row["context_id"]], row, gold, maps[row["encoding"]][row["context_id"]])
        if value.data.prompt != prompt: raise ValueError("frozen prompt changed")
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


def interface(output): return qnative.interface(output)


def verify():
    ready = read(ROOT / "READY.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]: raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("closure changed: " + path)
    if sha(ANALYSIS / "FINAL_SEAL.json") != "f3923f17e472b4ca1051e2448c7175de21f844832c5a822a323b980730c99430": raise ValueError("admission seal changed")
    return ready
