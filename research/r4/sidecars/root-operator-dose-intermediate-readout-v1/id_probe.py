"""Qualified exact12 first-action probe entry."""
import asyncio
import functools

import id_study as s


def parse_args(argv=None):
    return implementation().parse_args(argv)


@functools.lru_cache(maxsize=1)
def implementation():
    return s.load("intermediate_dose_source_probe", s.SOURCE / "dr_probe.py",
                  "c2023ffd1d4485807ed47ef15163ae5e0a26780b45c509d861898f0deb620c02",
                  {"dr_study": s})


def main(argv=None):
    asyncio.run(implementation().run(parse_args(argv)))


if __name__ == "__main__": main()
