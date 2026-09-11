"""V3 fixed6 readout with coherent identity and recovered binding."""
import asyncio
import recovery_readout as v1
import recovery_study_v3 as s
import recovery_binding_v3 as b


parse_args = v1.parse_args


def main():
    args = parse_args()
    import qs_collect as qualified
    qualified.s = s; qualified.b = b
    with s.aliases({"od_study": s, "od_binding": b}): module = qualified.implementation()
    module.s = s
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": b}):
        asyncio.run(module.run(args))


if __name__ == "__main__": main()

