"""Exact qualified 128-call/512-record metrics."""
import hashlib
from pathlib import Path
SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/metrics.py"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != "09aa59b6aa60a99d1d062612d2738800db7f94a68b020318233ac11fe8742ead":
    raise ValueError("metrics source changed")
exec(compile(raw, str(SOURCE), "exec"), globals())

