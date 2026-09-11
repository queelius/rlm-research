"""Fresh-context positional-anchor replication bindings."""

import contextlib
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PRIOR = SIDE / "leaf-mnli-positional-anchor-binding-v1"
LOADER = SIDE / "leaf-mnli-field-order-replication-v1"
BASE = SIDE / "leaf-mnli-correspondence-v1"
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
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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


if sha(PRIOR / "READY_RECOVERY.json") != "d02f4deec95ac6b4e31d5e5dd02c8f2857eff64cd17cb09f6bb30bb402526c22":
    raise ValueError("qualified positional READY changed")
qualified = load("position_anchor_new_context_qualified", PRIOR / "study.py", "642bf5ec4eefa0e4d7ebf8753f30c93f18a865846e8327017ce65565b64dc59b")
base = qualified.base
MODEL = qualified.MODEL
service = qualified.service
lifecycle = qualified.lifecycle


def tokenizer():
    return qualified.tokenizer()


def verify():
    qualified.verify()
    ready = read(READY_PATH)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("closure changed: " + path)
    return ready
