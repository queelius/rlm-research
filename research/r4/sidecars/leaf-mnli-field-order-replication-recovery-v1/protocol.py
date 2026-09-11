"""Exact scientific protocol reused under the attempt-002 namespace."""

import study as s

original = s.load(
    "field_order_recovery_protocol",
    s.ORIGINAL / "protocol.py",
    "d3e3c8d7f4d13a187c9a41c7a10f0dcf6f3a3aa552544389934754d9a8c31ede",
    {"study": s},
)
for name in dir(original):
    if not name.startswith("__"):
        globals()[name] = getattr(original, name)
