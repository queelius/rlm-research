"""Additive admission repair: keep the original AG module alias through qualification."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import core
import owner

ORIGINAL_CHECK = owner.check_admission


def check_admission(path, ready):
    # The qualifier imports train_ag lazily. Its source module alias must survive
    # that call, not merely creation of eval_owner's module object.
    with core.original.aliases({"ag_study": core.original}):
        return ORIGINAL_CHECK(path, ready)


def verify():
    original = core.verify()
    ready = core.read(core.ROOT / "READY_V2.json")
    if core.digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("V2 admission-repair identity differs")
    if ready["original_ready_sha256"] != core.sha(core.ROOT / "READY.json"):
        raise ValueError("original sealed trainer changed")
    for path, expected in ready["closure_sha256"].items():
        if core.sha(path) != expected:
            raise ValueError("V2 admission-repair closure changed: " + path)
    return original, ready


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "check-admission", "run"))
    parser.add_argument("--owner-seconds", type=int, default=5000)
    parser.add_argument("--admission-json", type=Path, default=core.ROOT / "ADMISSION.json")
    parser.add_argument("--resume-after", type=int, default=0)
    args = parser.parse_args()
    if args.command == "check-admission":
        if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
            raise ValueError("qualification preflight must hide CUDA")
        started = time.monotonic()
        previous = sys.modules.get("ag_study")
        receipt = check_admission(args.admission_json, core.verify())
        if sys.modules.get("ag_study") is not previous:
            raise ValueError("scoped alias was not restored")
        print(json.dumps({"actual_initial_qualification_passed": True,
            "admission_sha256": receipt["sha256"],
            "initial_qualified_result_sha256": receipt["initial_qualified_result_sha256"],
            "attempt_directory_exists": core.ATTEMPT.exists(), "GPU_launched": False,
            "module_alias_restored": True, "elapsed_seconds": time.monotonic() - started}, sort_keys=True))
        return
    original, ready = verify()
    if args.command == "verify":
        print(ready["identity"])
        return
    core.write_x(core.ROOT / f"V2_LAUNCH_AFTER_{args.resume_after:03d}.json", {
        "repair_ready_sha256": core.sha(core.ROOT / "READY_V2.json"),
        "original_ready_identity": original["identity"],
        "admission_sha256": core.sha(args.admission_json),
        "repair": "ag_study import alias scoped across actual complete admission qualification",
        "optimizer_or_probability_changes": False, "started_epoch": time.time()})
    previous = owner.check_admission
    owner.check_admission = check_admission
    try:
        result = owner.execute(args.owner_seconds, args.admission_json, args.resume_after)
    finally:
        owner.check_admission = previous
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["primary_endpoint_eligible"] else 1)


if __name__ == "__main__":
    main()
