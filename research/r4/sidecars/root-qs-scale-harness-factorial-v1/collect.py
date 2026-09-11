"""Qualified native collector for one 32-endpoint policy half."""

import argparse
import asyncio
import functools
from pathlib import Path

import study as s


@functools.lru_cache(maxsize=1)
def implementation():
    qualified = s.base.base
    path = qualified.OLD / "od_collect.py"
    module = qualified.load(
        "scale_harness_qualified_operator_collector",
        path,
        qualified.cf_ready["source_sha256"][str(path)],
        {"od_study": s, "od_protocol": s.protocol()},
    )
    with s.aliases({"od_study": s, "od_protocol": s.protocol(), "od_binding": s}):
        return module.implementation()


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("free",), required=True)
    parser.add_argument(
        "--plan", choices=("FREE_PLAN_UNCHANGED.json", "FREE_PLAN_SFT6.json"), required=True
    )
    for name in ("binding", "endpoint", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args(argv)
    if (args.start, args.stop) != (0, 32):
        raise ValueError("exact32 policy-half inventory")
    return args


def main():
    args = parse_args()
    module = implementation()
    module.s = s
    with s.aliases({"od_study": s, "od_protocol": s.protocol(), "od_binding": s}):
        asyncio.run(module.run(args))


if __name__ == "__main__":
    main()

