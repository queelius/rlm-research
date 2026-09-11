"""Unchanged positional-anchor protocol under the attempt-002 module graph."""

import recovery_study as s

module = s.load(
    "position_anchor_recovery_protocol",
    s.ROOT / "protocol.py",
    "413d8426dda09878ef77b3e16b126648c0b35a9c0fa6461dfd36e0048d2bb790",
    {"study": s},
)

for name in dir(module):
    if not name.startswith("__"):
        globals()[name] = getattr(module, name)
