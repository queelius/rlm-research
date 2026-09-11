"""Unchanged native readout with the exact training-only fixed6 binding."""
import asyncio
import recovery_readout as cli
import recovery_study_v3 as s
import postcapture_binding as b


def main():
    args = cli.parse_args()
    import qs_collect as qualified
    qualified.s = s
    qualified.b = b
    qualified.implementation.cache_clear()
    with s.aliases({'od_study': s, 'od_binding': b}):
        module = qualified.implementation()
    module.s = s
    with s.aliases({'od_study': s, 'od_protocol': qualified.p, 'od_binding': b}):
        asyncio.run(module.run(args))


if __name__ == '__main__':
    main()
