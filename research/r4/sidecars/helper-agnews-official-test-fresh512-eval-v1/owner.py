"""Exact qualified bounded owner, bound to four predeclared endpoints."""
import hashlib
from pathlib import Path
SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/owner.py"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != "c0a125fcdc6eb394f0ee6e216aac7e6a544d4fe337f3eac459af2281d4409ed8":
    raise ValueError("owner source changed")
exec(compile(raw, str(SOURCE), "exec"), globals())

