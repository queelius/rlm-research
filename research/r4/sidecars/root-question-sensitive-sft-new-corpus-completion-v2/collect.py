"""Unchanged metadata72 collector bound to completion-v2 checkpoint6."""
import asyncio
import recovery as r
import qs_collect as qualified


def main():
    study = r.readout_study()
    args = qualified.parse_args()
    qualified.s = study
    qualified.b = study
    qualified.implementation.cache_clear()
    with r.s.aliases({"od_study": study, "od_protocol": qualified.p, "od_binding": study}):
        module = qualified.implementation()
        module.s = study
        asyncio.run(module.run(args))


if __name__ == "__main__":
    main()
