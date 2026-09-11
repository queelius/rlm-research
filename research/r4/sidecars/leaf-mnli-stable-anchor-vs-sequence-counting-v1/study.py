"""Bindings for the prospective stable-anchor versus sequence-counting study."""

import contextlib
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PRIOR = SIDE / "leaf-mnli-positional-anchor-new-context-v1"
LOADER = SIDE / "leaf-mnli-field-order-replication-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
READY_PATH = ROOT / "READY.json"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")


def serialize(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@contextlib.contextmanager
def aliases(values):
    old = {key: sys.modules.get(key) for key in values}
    sys.modules.update(values)
    try:
        yield
    finally:
        for key, value in old.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value


def load(name, path, pin=None, aliases_map=None):
    if pin and sha(path) != pin:
        raise ValueError("source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with aliases(aliases_map or {}):
        spec.loader.exec_module(module)
    return module


prior = load(
    "stable_anchor_prior_study",
    PRIOR / "study.py",
    "c6fc8fd0c2ad67bc78b1c1b59eb000003e6c055ebc9d6748214d4ac9ee11407c",
)
base = prior.base
qualified = prior.qualified
BASE = prior.BASE
MODEL = prior.MODEL
service = prior.service
lifecycle = prior.lifecycle


def tokenizer():
    return prior.tokenizer()


def verify():
    prior.verify()
    ready = read(READY_PATH)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("closure changed: " + path)
    return ready
