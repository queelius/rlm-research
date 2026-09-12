"""Authoritative specialization of the audited fresh512 source-to-raw comparator."""

import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EVAL = HERE.parents[1] / "sidecars/helper-trec-retention-b4-eval-v1"
SOURCE = HERE.parents[1] / "sidecars/helper-agnews-fresh512-eval-v1/compare.py"
EXPECTED = "09dc0db5e3067a46dbdd992da82b775f311bed4822e83eb88bab32bdf6b9d127"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("audited fresh512 comparator source changed")
sys.path.insert(0, str(EVAL))
for name in ("collect", "eligibility", "metrics", "study"):
    sys.modules.pop(name, None)
text = raw.decode().replace(
    '"fresh512-source-to-raw-paired-audit-v1"',
    '"trec-retention-b4-source-to-raw-paired-audit-v1"',
)
text = text.replace("fresh512 c32", "TREC retention c32")
text = text.replace("fresh512 calls", "TREC retention calls")
exec(compile(text, str(SOURCE), "exec"), globals())

