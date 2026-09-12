"""Final additive receipt verifier for the fresh-process collector-path repair."""

import study


def verify():
    ready = study.read(study.ROOT / "READY_V3.json")
    if ready["parent_ready_v2_sha256"] != study.sha(study.ROOT / "READY_V2.json"):
        raise ValueError("READY_V2 parent changed")
    if ready["identity"] != study.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V3 identity mismatch")
    for path, pin in ready["closure_sha256"].items():
        if study.sha(path) != pin:
            raise ValueError("V3 closure changed: " + path)
    return ready
