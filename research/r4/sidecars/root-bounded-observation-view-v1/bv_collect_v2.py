"""Exact32 V2 collection through the unchanged qualified native collector."""
import asyncio
import functools
import bv_study_v2 as s


@functools.lru_cache(maxsize=1)
def implementation():
    # V1 already pins the exact qualified accumulation collector source.
    path = s.v1.BASE / "ae_collect.py"
    module = s.load(
        "bounded_view_v2_base_collector",
        path,
        s.v1.base_ready["source_sha256"][str(path)],
        {"ae_study": s},
    )
    with s.aliases({"ae_study": s}):
        return module.implementation()


def main():
    module = implementation()
    args = module.parse_args()
    if (args.mode, args.plan, args.start, args.stop) != ("free", "FREE_PLAN.json", 0, 32):
        raise ValueError("exact32 bounded-view V2 inventory")
    with s.aliases({"od_study": s, "od_protocol": s.protocol(), "od_binding": s, "ae_study": s}):
        asyncio.run(module.run(args))


if __name__ == "__main__":
    main()
