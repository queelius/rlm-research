"""Additive V4 receipt and attempt-002 facade for import-isolated recovery dependencies."""

import study as base


ATTEMPT = base.ROOT / "outputs/attempt-002"


def verify():
    ready = base.read(base.ROOT / "READY_V4.json")
    if ready["parent_ready_v3_sha256"] != base.sha(base.ROOT / "READY_V3.json"):
        raise ValueError("READY_V3 parent changed")
    if ready["identity"] != base.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V4 identity mismatch")
    for path, pin in ready["closure_sha256"].items():
        if base.sha(path) != pin: raise ValueError("V4 closure changed: " + path)
    return ready


def __getattr__(name): return getattr(base, name)
