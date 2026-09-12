"""Attempt-002 specialization of the preserved independent raw analyzer."""

import hashlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "root-qs6-budgeted-evidence-stop-independent-2026-09-12/analyze.py"
EXPECTED = "b0eb009e7cfb304902fd67545ad5852e194695ea54dbb30d51b67dfda1624531"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("preserved independent analyzer source changed")
text = raw.decode()
text = text.replace('SIDE / "outputs/attempt-001"', 'SIDE / "outputs/attempt-002"')
text = text.replace('READY = SIDE / "READY.json"', 'READY = SIDE / "READY_V2.json"')
text = text.replace(
    'READY_SHA256 = "27f4676a7e245459df2d24d62975e189060fd56a971a142281e2e6f227883360"',
    'READY_SHA256 = "3b74470df4d46f395d4fda8d1f9348853e0880e83c8bffe6c4cf5bae2a6f7ef2"',
)
text = text.replace(
    'READY_IDENTITY = "6e67e8efa22da7d34bc9bea1a9cb69ebadab79199e9043e769083174ef0a2407"',
    'READY_IDENTITY = "f8ec80255daf6776cf88db275dddb5751dd37005a42ae75182e0cba3fa988dd2"',
)
exec(compile(text, str(SOURCE), "exec"), globals())

