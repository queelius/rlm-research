"""Exact qualified native collector bound to the new frozen schedule."""
import hashlib
from pathlib import Path
SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/collect.py"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != "987eefb0c1aea3afa42167f4339f55a6229b6f636377d7fb0c04d99854e97ccf":
    raise ValueError("collector source changed")
exec(compile(raw, str(SOURCE), "exec"), globals())

