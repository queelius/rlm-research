"""Exact audited raw comparator extended to all predeclared seed pairs."""
import hashlib
from pathlib import Path
SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/compare.py"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != "09dc0db5e3067a46dbdd992da82b775f311bed4822e83eb88bab32bdf6b9d127":
    raise ValueError("raw comparator source changed")
text = raw.decode().replace(
    '(("c32", "rl_step8"), ("c32", "sft_step8"), ("rl_step8", "sft_step8"))',
    '(("c32", "rl_step8"), ("c32", "sft_step8"), ("c32", "rl_seed2_step8"), ("rl_step8", "sft_step8"), ("rl_step8", "rl_seed2_step8"), ("sft_step8", "rl_seed2_step8"))',
)
text = text.replace('"fresh512-source-to-raw-paired-audit-v1"', '"agnews-official-test-fresh512-source-to-raw-paired-audit-v1"')
exec(compile(text, str(SOURCE), "exec"), globals())

