"""Thin exact owner adaptation for the bounded DBpedia-224 screen."""

import hashlib
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/owner.py"
SOURCE_SHA256 = "c0a125fcdc6eb394f0ee6e216aac7e6a544d4fe337f3eac459af2281d4409ed8"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
    raise ValueError("qualified source owner changed")
text = raw.decode()
replacements = {
    "fresh512": "DBpedia224",
    '"planned_calls": 128': '"planned_calls": 56',
    '"planned": 128': '"planned": 56',
    '"planned_records": 512': '"planned_records": 224',
    "exact900 cap and unused arm attempt required": "exact700 cap and unused arm attempt required",
}
expected = {
    "fresh512": 2,
    '"planned_calls": 128': 2,
    '"planned": 128': 1,
    '"planned_records": 512': 2,
    "exact900 cap and unused arm attempt required": 1,
}
for before, after in replacements.items():
    if text.count(before) != expected[before]:
        raise ValueError("qualified owner transform seam changed: " + before)
    text = text.replace(before, after)
exec(compile(text, str(SOURCE) + ":dbpedia224", "exec"), globals())

