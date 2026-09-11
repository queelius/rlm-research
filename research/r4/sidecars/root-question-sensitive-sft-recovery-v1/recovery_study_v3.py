"""Coherent V3 identity facade used at every recovery process boundary."""
from contextlib import contextmanager
import recovery_study as v1

SOURCE_ROOT, ROOT, SIDE, ORIGINAL, ORIGINAL_ATTEMPT, ATTEMPT = (
    v1.SOURCE_ROOT, v1.ROOT, v1.SIDE, v1.ORIGINAL, v1.ORIGINAL_ATTEMPT, v1.ATTEMPT)
read, write, sha, digest, aliases, load = v1.read, v1.write, v1.sha, v1.digest, v1.aliases, v1.load
NATIVE, TRAIN, OLD, CT, CF, JOINT, CHILD_SHA = v1.NATIVE, v1.TRAIN, v1.OLD, v1.CT, v1.CF, v1.JOINT, v1.CHILD_SHA
base, NAMESPACE, SEED = v1.base, v1.NAMESPACE, v1.SEED
capture_boundary, missing_indices, train_plan, learning = v1.capture_boundary, v1.missing_indices, v1.train_plan, v1.learning
starting_policy, runtime, baseline_reference = v1.starting_policy, v1.runtime, v1.baseline_reference


def __getattr__(name): return getattr(v1, name)


def verify():
    ready = read(SOURCE_ROOT / "READY_v3.json")
    if digest({k: value for k, value in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY_v3 identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("READY_v3 changed " + path)
    capture_boundary(); starting_policy(); return ready


@contextmanager
def _v3_identity():
    old = v1.verify; v1.verify = verify
    try: yield
    finally: v1.verify = old


def build_corpus_ready():
    with _v3_identity(): return v1.build_corpus_ready()


def corpus(limit=None):
    with _v3_identity(): return v1.corpus(limit)

