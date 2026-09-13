"""Additive runtime repair: expose the clock required by inherited Collector.call."""

import time

from study import *  # noqa: F403
import study as base

READY = ROOT / "READY_CALL_REPAIR.json"  # noqa: F405
ATTEMPT = ROOT / "outputs/attempt-002"  # noqa: F405
now = time.time


def verify():
    ready = read(READY)  # noqa: F405
    assert ready["identity"] == digest({k: v for k, v in ready.items() if k != "identity"})  # noqa: F405
    for path, expected in ready["closure_sha256"].items():
        assert sha(path) == expected, path  # noqa: F405
    assert len(roots()) == 4 and len(calls()) == 8  # noqa: F405
    binding()  # noqa: F405
    return ready

