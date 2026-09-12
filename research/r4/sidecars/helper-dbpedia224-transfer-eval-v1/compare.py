"""Audited source-to-raw four-arm DBpedia comparator."""

import hashlib
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-official-test-fresh512-eval-v1/compare.py"
SOURCE_SHA256 = "af6b5bcfd08fd0d18a8467812ce930ec29471b235099ec6bde14083e4edd99fd"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
    raise ValueError("audited four-arm comparator source changed")
text = raw.decode()
text = text.replace("agnews-official-test-fresh512", "dbpedia224-transfer")
text = text.replace("fresh512 c32", "DBpedia224 c32")
text = text.replace("fresh512 calls", "DBpedia224 calls")
exec(compile(text, str(SOURCE) + ":dbpedia224", "exec"), globals())
