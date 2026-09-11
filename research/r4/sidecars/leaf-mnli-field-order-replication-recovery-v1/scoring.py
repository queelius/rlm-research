"""Exact field-order scorer reused without scientific changes."""

import protocol as p
import study as s

original = s.load(
    "field_order_recovery_scoring",
    s.ORIGINAL / "scoring.py",
    "de338539f4278ac311fbdcdafbc75e9e0124e85dcb30bac90e4751882258ca58",
    {"study": s, "protocol": p},
)
for name in dir(original):
    if not name.startswith("__"):
        globals()[name] = getattr(original, name)
