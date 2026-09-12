"""Bounded three-arm TREC retention owner, specialized from the qualified evaluator."""

import hashlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/owner.py"
EXPECTED = "c0a125fcdc6eb394f0ee6e216aac7e6a544d4fe337f3eac459af2281d4409ed8"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("qualified owner source changed")
text = raw.decode().replace("fresh512", "TREC retention")
text = text.replace("exact900", "exact600")
text = text.replace('"planned_calls": 128', '"planned_calls": 32')
text = text.replace('"planned_records": 512', '"planned_records": 128')
text = text.replace('"planned": 128', '"planned": 32')
text = text.replace('"planned_calls": 128', '"planned_calls": 32')
exec(compile(text, str(SOURCE), "exec"), globals())

