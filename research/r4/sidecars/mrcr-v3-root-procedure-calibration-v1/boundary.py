"""Bind only the frozen calibration context into the qualified rootless runtime."""

import hashlib
import os
from pathlib import Path
import sys

import study


def bind(argv, context):
    if not argv or argv[0] != "run": return argv
    if any(value in {"--mount", "-v", "--volume", "--volumes-from"}
            or value.startswith(("--mount=", "--volume=", "--volumes-from=")) for value in argv):
        raise ValueError("additional mounts forbidden")
    context = Path(context)
    expected = (study.ROOT / "inputs/contexts").resolve()
    if (context.is_symlink() or context.absolute() != context.resolve()
            or context.parent.resolve() != expected or not context.is_file()
            or hashlib.sha256(context.read_bytes()).hexdigest() != context.stem):
        raise ValueError("only the frozen calibration context may be mounted")
    return ["run", "--mount", f"type=bind,source={context},destination=/context.txt,ro=true", *argv[1:]]


if __name__ == "__main__":
    target = Path(os.environ["MRCR_CALIBRATION_CONTEXT"])
    docker = study.SIDE / "rootless-runtime-feasibility-v1/bin/docker"
    args = bind(sys.argv[1:], target)
    os.execv(str(docker), [str(docker), *args])

