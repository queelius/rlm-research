"""Qualified free collector for recovered fixed6 only."""
import argparse
import asyncio
from pathlib import Path
import recovery_study as s
import recovery_binding as b


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", choices=("FREE_PLAN.json", "DEV_PLAN.json"), required=True)
    for name in ("binding", "endpoint", "output"):
        ap.add_argument("--" + name, type=Path, required=True)
    ap.add_argument("--stop", type=int, choices=(8, 72), required=True)
    ap.add_argument("--deadline", type=float, required=True)
    args = ap.parse_args(argv); args.mode = "free"; args.start = 0
    if (args.plan, args.stop) not in (("DEV_PLAN.json", 8), ("FREE_PLAN.json", 72)):
        raise ValueError("exact recovered readout inventory")
    return args


def main():
    args = parse_args()
    import qs_collect as qualified
    qualified.s = s; qualified.b = b
    module = qualified.implementation()
    module.s = s
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": b}):
        asyncio.run(module.run(args))


if __name__ == "__main__": main()

