"""Attempt-002 owner; only launcher identity and output namespace change."""

import argparse
from pathlib import Path

import protocol_v2 as p
import recovery_study as s


module = s.load(
    "position_anchor_recovery_owner",
    s.ROOT / "owner.py",
    "b0610099e2a66735979d461e894191d76db4e71b3393966aa5883dd0a904bcd4",
    {"study": s, "protocol": p},
)
CLOCK = module.CLOCK
credential = module.credential
binding = module.binding
preflight = module.preflight


def validate_argv(argv):
    expected = [str(s.NATIVE), str(s.ROOT / "collect_v2.py"), "run", "--endpoint"]
    if len(argv) != 9 or argv[:4] != expected or argv[5] != "--output" or argv[7] != "--deadline":
        raise ValueError("exact recovery collector CLI required")
    endpoint, output = Path(argv[4]), Path(argv[6])
    if endpoint.resolve() != s.ATTEMPT / "owned-service/service/endpoint-original.json" or output.resolve() != s.ATTEMPT / "rollout":
        raise ValueError("exact attempt-002 namespace required")
    return {"endpoint": endpoint, "output": output, "deadline": float(argv[8])}


def collector_argv(stage, output, deadline):
    argv = [str(s.NATIVE), str(s.ROOT / "collect_v2.py"), "run", "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(output / "rollout"), "--deadline", str(deadline)]
    validate_argv(argv)
    return argv


def suite():
    value = s.base.load(
        "position_anchor_recovery_suite",
        s.SIDE / "leaf-post-sft-suite-v1/suite.py",
        "6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1",
    )
    value.verify()
    s.lifecycle.install(value)
    value.preflight = preflight
    value.SERVE = s.ROOT / "service_wrapper_v2.py"
    value.life.__dict__["ALLOCATION_SERVICE"] = value.SERVE
    return value


module.validate_argv = validate_argv
module.collector_argv = collector_argv
module.suite = suite
execute = module.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT)
    args = parser.parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        result = execute(args.output)
        print(result)
        raise SystemExit(0 if result["complete"] else 1)
