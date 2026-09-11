"""V2 owner: unchanged fixed32 clocks, additive attempt-002/collector binding."""
import argparse
from pathlib import Path

import bv_study_v2 as s

old = s.load(
    "bounded_view_v2_owner_base",
    s.ROOT / "bv_owner.py",
    s.v1_ready["source_sha256"][str(s.ROOT / "bv_owner.py")],
    {"bv_study": s},
)


def collector_argv(stage, destination, deadline):
    return [
        str(s.NATIVE), str(s.ROOT / "bv_collect_v2.py"), "--mode", "free",
        "--plan", "FREE_PLAN.json", "--start", "0", "--stop", "32",
        "--binding", str(stage / "BINDING.json"),
        "--endpoint", str(stage / "service/endpoint-original.json"),
        "--output", str(destination), "--deadline", str(float(deadline)),
    ]


old.collector_argv = collector_argv
execute, harvest, ledger, dependencies = old.execute, old.harvest, old.ledger, old.dependencies


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        result = execute(args.output)
        print({"complete": result["complete"], "errors": result["error"]})
        raise SystemExit(0 if result["complete"] else 1)
