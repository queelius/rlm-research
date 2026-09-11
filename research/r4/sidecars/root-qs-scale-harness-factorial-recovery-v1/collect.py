"""Qualified collector entry with the corrected complete study/protocol surfaces."""

import argparse
import asyncio
import functools
import study as s


original = s.load(
    "scale_harness_recovery_original_collect",
    s.ORIGINAL / "collect.py",
    "ca89f38d788796b734cf6134d6ce10832bb61fc0809ce69877be7cfba7cf2251",
    {"study": s},
)
parse_args = original.parse_args


@functools.lru_cache(maxsize=1)
def implementation():
    with s.aliases({"od_study": s, "od_protocol": s.protocol(), "od_binding": s}):
        module = original.implementation()
        module.s = s
        module.p = s.protocol()
        module.b = s
        return module


def main():
    args = parse_args()
    module = implementation()
    with s.aliases({"od_study": s, "od_protocol": s.protocol(), "od_binding": s}):
        asyncio.run(module.run(args))


if __name__ == "__main__":
    main()

