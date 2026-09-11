"""V2 free collector with recovered binding validation in the lazy import scope."""
import asyncio
import recovery_readout as v1
import recovery_study as s
import recovery_binding_v2 as b


def main():
    args = v1.parse_args()
    import qs_collect as qualified
    qualified.s = s; qualified.b = b
    with s.aliases({"od_binding": b}): module = qualified.implementation()
    module.s = s
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": b}):
        asyncio.run(module.run(args))


if __name__ == "__main__": main()

