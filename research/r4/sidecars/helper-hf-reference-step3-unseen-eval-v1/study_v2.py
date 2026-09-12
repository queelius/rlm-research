"""Additive collector-interface repair for the reference checkpoint-3 evaluator."""

import study as base


# The reused c32 collector reads this at response normalization time.
CHILD_ALIAS = base.source.CHILD_ALIAS


def binding(): return base.binding()


def verify(require_training=True):
    ready = base.read(base.ROOT / "READY_V2.json")
    if ready.get("status") != "CPU_READY_REFERENCE_MATCHED_THREE_UPDATE_CONTROL_V2":
        raise ValueError("unexpected V2 READY status")
    if base.digest({k: v for k, v in ready.items() if k != "identity"}) != ready.get("identity"):
        raise ValueError("V2 READY identity differs")
    for path, expected in ready["closure_sha256"].items():
        if base.sha(path) != expected: raise ValueError("V2 closure changed: " + path)
    if base.digest(base.schedule()) != ready["schedule_sha256"]:
        raise ValueError("fixed256 schedule changed")
    if require_training: base.qualify()
    return ready


def __getattr__(name): return getattr(base, name)
