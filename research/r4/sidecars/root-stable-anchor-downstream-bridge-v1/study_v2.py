"""Additive V2 facade preserving V1 READY and sources."""

import functools
from types import SimpleNamespace

import protocol_v2 as p
import study as old

ROOT, SIDE, SCALE, STABLE, ANALYSIS, NATIVE = old.ROOT, old.SIDE, old.SCALE, old.STABLE, old.ANALYSIS, old.NATIVE
ORIGINAL = old.ORIGINAL
ATTEMPT = ROOT / "outputs/attempt-002"
INPUTS = ROOT / "inputs-v3"
RUNTIME_ROOT = ROOT / "runtime-v2"
read, write, sha, digest, aliases, load = old.read, old.write, old.sha, old.digest, old.aliases, old.load
scale, stable, base, qnative, JOINT, LABELS, corpus = old.scale, old.stable, old.base, old.qnative, old.JOINT, old.LABELS, old.corpus
ACTIVE_MAPS = None
BASE_ALIAS = str(qnative.stack().prior.BASE)


def runtime(): return old.runtime()
def protocol(): return old.protocol()
def answer(records, gold, row): return p.reduce_answer({"records": records}, gold, row["question"])


def binding():
    value = old.binding()
    value["stable_anchor_downstream_bridge_v2"] = {"leaf_calls": 24, "root_episodes": 96,
        "leaf_model": BASE_ALIAS, "encodings": list(p.ENCODINGS), "root": "qs6", "no_training": True}
    return value


def validate(value, descriptor, path):
    if value != binding(): raise ValueError("V2 binding changed")
    old.validate(old.binding(), descriptor, path)


def make_task(context, row, gold, predicted):
    value = old.make_task(context, row, gold, predicted)
    broken_setup, broken_finalize = value.setup, value.finalize
    async def setup(trace, runtime): await broken_setup(trace, runtime)
    async def finalize(trace, runtime): await broken_finalize(trace, runtime)
    value.setup, value.finalize = setup, finalize
    return value


@functools.lru_cache(maxsize=1)
def stack():
    native = qnative.stack().native
    plan = {row["id"]: row for row in read(INPUTS / "ROOT_PLAN.json")}
    public = {row["id"]: row for row in read(INPUTS / "PUBLIC.json")}
    if ACTIVE_MAPS is None: raise ValueError("leaf maps not acquired before root stack")
    def task(context, prompt, gold, name):
        row = plan[name]; value = make_task(public[row["context_id"]], row, gold, ACTIVE_MAPS[row["encoding"]][row["context_id"]])
        if value.data.prompt != prompt: raise ValueError("V2 frozen root prompt changed")
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


def interface(output): return old.interface(output)


def verify():
    old.verify()
    ready = read(ROOT / "READY_V3.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]: raise ValueError("V2 READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("V2 closure changed: " + path)
    return ready
