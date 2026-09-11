"""Unchanged whole-contract scorer under the attempt-002 module graph."""

import protocol_v2 as p
import recovery_study as s

module = s.load(
    "position_anchor_recovery_scoring",
    s.ROOT / "scoring.py",
    "e7c7c1d38350bb77d0c6afee8e5a9e378be7e824ada4f750f20700aec5301907",
    {"study": s, "protocol": p},
)

for name in dir(module):
    if not name.startswith("__"):
        globals()[name] = getattr(module, name)
