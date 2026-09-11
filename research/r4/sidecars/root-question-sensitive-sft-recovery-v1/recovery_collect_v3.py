"""V3 missing-tail collector with coherent READY identity."""
import asyncio
import recovery_collect as v1
import recovery_study_v3 as s


parse_args = v1.parse_args


def main():
    args = parse_args()
    import qs_collect as qualified
    qualified.s = s
    with s.aliases({"od_study": s}): module = qualified.implementation()
    module.s = s
    with s.aliases({"od_study": s, "od_protocol": qualified.p, "od_binding": qualified.b}):
        asyncio.run(module.run(args))


if __name__ == "__main__": main()

