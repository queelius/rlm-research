"""Attempt-002 namespace over the immutable failed-prelaunch field-order replication."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / "leaf-mnli-field-order-replication-v1"
spec = importlib.util.spec_from_file_location("field_order_recovery_original_study", ORIGINAL / "study.py")
prior = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = prior
spec.loader.exec_module(prior)

SIDE = prior.SIDE
QUALIFIED = prior.QUALIFIED
SOURCE = prior.SOURCE
FIELD_ORDER = prior.FIELD_ORDER
BASE = prior.BASE
NATIVE = prior.NATIVE
MODEL = prior.MODEL
service = prior.service
lifecycle = prior.lifecycle
qualified = prior.qualified
ALIEN = qualified.ALIEN
ATTEMPT = ROOT / "outputs/attempt-002"
READY_PATH = ROOT / "READY.json"
sha, read, write, serialize, digest, aliases, load = (
    prior.sha,
    prior.read,
    prior.write,
    prior.serialize,
    prior.digest,
    prior.aliases,
    prior.load,
)
base = prior.base


def tokenizer():
    return prior.tokenizer()


def verify():
    prior.verify()
    ready = read(READY_PATH)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("recovery READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError("recovery closure changed: " + path)
    return ready

