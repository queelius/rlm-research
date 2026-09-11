"""Qualified native metadata72 collector for the new-corpus checkpoint."""
import asyncio
import rep_readout_study as s
import qs_collect as qualified


def main():
    args = qualified.parse_args()
    qualified.s = s; qualified.b = s; qualified.implementation.cache_clear()
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": s}):
        module = qualified.implementation(); module.s = s
        asyncio.run(module.run(args))


if __name__ == "__main__": main()
