"""Additive attempt-002 namespace over immutable positional-anchor inputs."""

from pathlib import Path

import study as original


ROOT = original.ROOT
SIDE = original.SIDE
PRIOR = original.PRIOR
QUALIFIED = original.QUALIFIED
NATIVE = original.NATIVE
MODEL = original.MODEL
qualified = original.qualified
base = original.base
service = original.service
lifecycle = original.lifecycle
ATTEMPT = ROOT / "outputs/attempt-002"
READY_PATH = ROOT / "READY_RECOVERY.json"
sha = original.sha
read = original.read
write = original.write
serialize = original.serialize
digest = original.digest
aliases = original.aliases
load = original.load
tokenizer = original.tokenizer


def verify():
    original.verify()
    ready = read(READY_PATH)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("recovery READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin:
            raise ValueError(f"recovery closure changed: {path}")
    return ready
