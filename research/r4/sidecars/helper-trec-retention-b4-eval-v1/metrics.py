"""Exact 32-call/128-record retention accounting."""

import hashlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/metrics.py"
EXPECTED = "09aa59b6aa60a99d1d062612d2738800db7f94a68b020318233ac11fe8742ead"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("qualified metrics source changed")
text = raw.decode()
text = text.replace('LABELS = ("World", "Sports", "Business", "Sci/Tech")', 'LABELS = ("human being", "location", "abbreviation", "entity", "description and abstract concept", "numeric value")')
text = text.replace("agnews-fresh512-result-v1", "trec-retention-b4-result-v1")
text = text.replace("fixed128call/512gold", "fixed32call/128gold")
text = text.replace("len(schedule) != 128", "len(schedule) != 32")
text = text.replace("len(expected_ids) != 512", "len(expected_ids) != 128")
text = text.replace("len(calls) == 128", "len(calls) == 32")
text = text.replace("len(predictions) == 512", "len(predictions) == 128")
text = text.replace('"expected_calls": 128', '"expected_calls": 32')
text = text.replace('"expected_ids": 512', '"expected_ids": 128')
text = text.replace('"unattempted_calls": 128', '"unattempted_calls": 32')
text = text.replace('"unavailable_predictions": 512', '"unavailable_predictions": 128')
text = text.replace("correct / 512", "correct / 128")
text = text.replace("len(differences) == 128", "len(differences) == 32")
text = text.replace("range(128)", "range(32)")
text = text.replace("/ 512", "/ 128")
text = text.replace('"paired_unavailable": 512', '"paired_unavailable": 128')
text = text.replace('"planned_clusters": 128', '"planned_clusters": 32')
text = text.replace("fixed512 local-exposure-heldout AG train split; base pretraining unknown", "historically evaluated retained TREC test partition; not fresh generalization")
text = text.replace("shared four-record native request; not512 independent items", "shared four-record native request; not128 independent items")
exec(compile(text, str(SOURCE), "exec"), globals())
