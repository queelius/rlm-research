"""Serially collect only the frozen missing tail, indices65..71."""
import argparse
import asyncio
from pathlib import Path
import recovery_study as s


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    for name in ("binding", "endpoint", "output"):
        ap.add_argument("--" + name, type=Path, required=True)
    ap.add_argument("--deadline", type=float, required=True)
    args = ap.parse_args(argv)
    args.mode = "capture"; args.plan = "TRAIN_PLAN.json"; args.start = 65; args.stop = 72
    return args


def main():
    args = parse_args()
    import qs_collect as qualified
    qualified.s = s
    module = qualified.implementation()
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": qualified.b}):
        asyncio.run(module.run(args))


if __name__ == "__main__": main()

