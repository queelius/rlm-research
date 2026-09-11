"""Qualified released-base service under the positional-anchor namespace."""

import study as s


def main():
    wrapper = s.load(
        "position_anchor_qualified_service",
        s.PRIOR / "service_wrapper_v2.py",
        "43e502086e816735431f214f97c15929ef7cda037cf69d576a055f4ecb5dda97",
        {"study": s.qualified},
    )
    wrapper.main()


if __name__ == "__main__":
    main()
