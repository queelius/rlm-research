"""Attempt-003 binding for the lifecycle-only repair."""

from study_v2 import *  # noqa: F403

READY = ROOT / "READY_LIFECYCLE_REPAIR.json"  # noqa: F405
ATTEMPT = ROOT / "outputs/attempt-003"  # noqa: F405


def verify():
    ready = read(READY)  # noqa: F405
    assert ready["identity"] == digest({k: v for k, v in ready.items() if k != "identity"})  # noqa: F405
    for path, expected in ready["closure_sha256"].items():
        assert sha(path) == expected, path  # noqa: F405
    assert len(roots()) == 4 and len(calls()) == 8  # noqa: F405
    binding()  # noqa: F405
    return ready

