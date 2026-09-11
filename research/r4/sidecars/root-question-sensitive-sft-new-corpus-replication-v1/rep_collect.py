"""Qualified genuine c32 teacher capture for the frozen new corpus."""
import asyncio
import rep_study as s
import rep_binding as b
import qs_collect as qualified


def main():
    args = qualified.parse_args()
    qualified.s = s; qualified.b = b; qualified.implementation.cache_clear()
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": b}):
        module = qualified.implementation(); module.s = s
        asyncio.run(module.run(args))


if __name__ == "__main__": main()
