"""Additive READY_V2 verifier; V1 remains immutable evidence of the caught defect."""

import study as v1


def verify():
    ready = v1.read(v1.ROOT / "READY_V2.json")
    if ready["parent_ready_sha256"] != v1.sha(v1.ROOT / "READY.json"):
        raise ValueError("V1 parent receipt changed")
    if ready["identity"] != v1.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V2 identity mismatch")
    for path, pin in ready["closure_sha256"].items():
        if v1.sha(path) != pin:
            raise ValueError("V2 closure changed: " + path)
    return ready
