"""Qualified native QS collector rebound to fresh inputs and three policy bindings."""
import asyncio
import study as s

_old = list(s.sys.path)
try:
    s.sys.path.insert(0, str(s.ORIGINAL))
    import qs_collect as qualified
finally:
    s.sys.path[:] = _old


def main():
    args = qualified.parse_args()
    qualified.s = s; qualified.b = s; qualified.implementation.cache_clear()
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": s}):
        module = qualified.implementation(); module.s = s
        asyncio.run(module.run(args))


if __name__ == "__main__":
    main()
