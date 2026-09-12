"""TREC specialization of the qualified raw native collector."""

import hashlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/collect.py"
EXPECTED = "987eefb0c1aea3afa42167f4339f55a6229b6f636377d7fb0c04d99854e97ccf"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("qualified collector source changed")
text = raw.decode().replace('"fresh512_qualified_native_decoder"', '"trec_retention_native_decoder"')
text = text.replace('"ag_news"', '"trec"')
exec(compile(text, str(SOURCE), "exec"), globals())

