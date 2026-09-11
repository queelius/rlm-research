"""Unchanged campaign optimizer/loss, with the explicitly amended native proof route."""

import argparse
import json
import subprocess
import traceback
import types
import uuid
from pathlib import Path

import common as a
import campaign_train as trainer

c = a.c
ORIGINAL_AUTHENTICATE = trainer.authenticate_group
ORIGINAL_SUBPROCESS = trainer.subprocess


def native_proof_command(command):
    expected = [str(c.NATIVE_PYTHON), str(a.OLD / "campaign_native.py"), "verify-export", "--output"]
    if not isinstance(command, list) or len(command) != 5 or command[:4] != expected:
        raise ValueError("unexpected native verifier dispatch; no broad subprocess rewrite")
    return [command[0], str(a.ROOT / "native_amendment.py"), *command[2:]]


def authenticate_group(group_path, generation_path):
    amendment = a.verify_amendment()
    manifest = c.read(Path(group_path).parent / "MANIFEST.json")
    if manifest.get("continuation_amendment_id") != amendment["amendment_id"]:
        raise ValueError("training group is not from this amendment")
    def run_native(command, **kwargs):
        return subprocess.run(native_proof_command(command), **kwargs)
    # Replace only this module's subprocess handle, not the shared subprocess module.
    trainer.subprocess = types.SimpleNamespace(run=run_native)
    try:
        group, generation, identity = ORIGINAL_AUTHENTICATE(group_path, generation_path)
    finally:
        trainer.subprocess = ORIGINAL_SUBPROCESS
    if not 4 <= generation["round"] <= 8:
        raise ValueError("continuation may train only original generations4..8")
    identity["continuation"] = {"amendment_id": amendment["amendment_id"],
        "amendment_sha256": c.file_hash(a.ROOT / "AMENDMENT.json"),
        "trainer_wrapper_sha256": c.file_hash(Path(__file__)), "original_trainer_sha256": c.file_hash(Path(trainer.__file__)),
        "native_verifier": str(a.ROOT / "native_amendment.py"), "new_global_cap_seconds": a.CAP_SECONDS}
    identity["identity"] = c.digest({k: v for k, v in identity.items() if k != "identity"})
    return group, generation, identity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deadline", type=float, default=float("inf"))
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    trainer.authenticate_group = authenticate_group
    try:
        print(json.dumps(trainer.train(args), sort_keys=True, allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            c.write_once(args.output.parent / ("TRAIN_FAILURE-" + uuid.uuid4().hex + ".json"),
                {"type": type(error).__name__, "error": str(error), "traceback": traceback.format_exc(), "checkpoint_preserved": True})
        raise


if __name__ == "__main__":
    main()
