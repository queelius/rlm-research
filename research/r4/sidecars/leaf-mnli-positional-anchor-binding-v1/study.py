"""Position-anchor MNLI factorial using the qualified released-base service."""

import contextlib
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PRIOR = SIDE / "leaf-mnli-host-identifier-join-v1"
QUALIFIED_READY_SHA = "aa43efb5134f8ed909128bf22caa23c210757406ef8f105e027c7afe61c13e6d"
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
        raise ValueError(f"source changed: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with aliases(aliases_map or {}):
        spec.loader.exec_module(module)
    return module


if sha(PRIOR / "READY_v2.json") != QUALIFIED_READY_SHA:
    raise ValueError("qualified host-join READY changed")
qualified = load(
    "position_anchor_qualified_study",
    PRIOR / "study.py",
    "49636128868f1e0e391927e3aaee878b1aa84a6c164e71abf0e618bd21f37596",
)
base = qualified.base
MODEL = qualified.MODEL
service = qualified.service
lifecycle = qualified.lifecycle
QUALIFIED = qualified.QUALIFIED


def tokenizer():
    return qualified.tokenizer()


def verify():
    ready = read(READY_PATH)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError(f"closure changed: {path}")
    return ready
