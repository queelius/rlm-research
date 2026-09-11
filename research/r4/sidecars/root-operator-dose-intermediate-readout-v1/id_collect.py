"""Qualified exact16 collector entry."""
import argparse
import asyncio
import functools
from pathlib import Path

import id_study as s


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", choices=tuple(f"FREE_PLAN_{policy}.json" for policy in ("sft6", "sft12", "sft18", "sft24")), required=True)
    for name in ("binding", "endpoint", "output"): parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--start", type=int, required=True); parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args(argv)
    if (args.start, args.stop) != (0, 16): raise ValueError("exact frozen16 only")
    args.mode = "free"
    return args


@functools.lru_cache(maxsize=1)
def implementation():
    qualified = s.load("intermediate_dose_source_collector", s.SOURCE / "dr_collect.py",
                       "513139140567eb72c283e451b7ec8f547be8096d49083e76801935eea44d995f",
                       {"dr_study": s})
    aliases = {"dr_study": s, "od_study": s, "od_protocol": s.protocol(), "od_binding": s}
    with s.aliases(aliases): return qualified.implementation()


def main(argv=None):
    args = parse_args(argv)
    aliases = {"dr_study": s, "od_study": s, "od_protocol": s.protocol(), "od_binding": s}
    with s.aliases(aliases): asyncio.run(implementation().run(args))


if __name__ == "__main__": main()
