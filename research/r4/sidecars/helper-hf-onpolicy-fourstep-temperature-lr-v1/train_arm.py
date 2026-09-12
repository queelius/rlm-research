"""Launch one sealed four-update arm from original c32."""

import argparse
import json
from pathlib import Path

import arm_runtime
import study


def run(arm_name, output, cap_seconds):
    ready = study.verify(arm_name)
    arm = study.ARMS[arm_name]
    if output.resolve() != (arm["root"] / "outputs/attempt-001").resolve():
        raise ValueError("exact sealed arm output required")
    if cap_seconds != study.CAP:
        raise ValueError("exact 4200-second owner cap required")
    source = arm_runtime.load_source()
    runtime = arm_runtime.install(source, arm)
    result = source.run(output, cap_seconds)
    paths = sorted(runtime["temperature_paths"])
    if paths != ["replay", "rollout"]:
        raise RuntimeError("both live rollout and replay temperature paths were not exercised")
    receipt = {
        "schema": "helper-hf-fourstep-arm-runtime-receipt-v1",
        "ready_identity": ready["identity"],
        "experimental_arm": {
            "name": arm_name,
            "temperature": arm["temperature"],
            "learning_rate": arm["learning_rate"],
        },
        "temperature_paths": paths,
        "poststep_extra_forward_sweep": False,
    }
    study.write(output / "ARM_RUNTIME_RECEIPT.json", receipt)
    result["arm_runtime_receipt"] = str(output / "ARM_RUNTIME_RECEIPT.json")
    result["arm_runtime_receipt_sha256"] = study.sha(output / "ARM_RUNTIME_RECEIPT.json")
    study.write(output / "RESULT.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=tuple(study.ARMS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.arm, arguments.output, arguments.cap_seconds), sort_keys=True))
