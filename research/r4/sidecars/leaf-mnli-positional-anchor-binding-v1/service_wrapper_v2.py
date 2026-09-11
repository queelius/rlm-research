"""Additive launcher-identity recovery for the unchanged 96-call study."""

from pathlib import Path

import recovery_study as s


def main():
    wrapper = s.load(
        "position_anchor_recovery_qualified_service",
        s.PRIOR / "service_wrapper_v2.py",
        "43e502086e816735431f214f97c15929ef7cda037cf69d576a055f4ecb5dda97",
        {"study": s.qualified},
    )
    # The qualified launcher hashes module.__file__. Bind that evidence to the
    # wrapper actually registered by the allocation lifecycle.
    wrapper.__file__ = str(Path(__file__).resolve())
    wrapper.main()


if __name__ == "__main__":
    main()
