"""Own the additive V2 native collection and unchanged qualification-only scorer."""

import argparse
import importlib.util
import json

import collect
import study


_spec = importlib.util.spec_from_file_location(
    "fresh_helper_qualification_v1_owner", study.V1_ROOT / "owner.py"
)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
base.study = study
base.collect = collect
base.SERVICE_WRAPPER = study.SERVICE_WRAPPER

dependencies = base.dependencies
attest_engine = base.attest_engine
finalize_kernel_attestation = base.finalize_kernel_attestation
arm_hf_deadline = base.arm_hf_deadline
execute = base.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    arguments = parser.parse_args()
    if arguments.command == "verify":
        print(study.verify()["identity"])
    else:
        result = execute(arguments.outer_seconds)
        print(json.dumps(result))
        raise SystemExit(0 if result["complete"] else 1)
