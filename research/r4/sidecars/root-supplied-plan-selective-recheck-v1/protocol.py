"""Qualified native scoring plus strict no-fallback selected-label merge."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "root-lambda-supplied-plan-ceiling-v1/protocol.py"
spec = importlib.util.spec_from_file_location("selective_recheck_ceiling_protocol", SOURCE)
source = importlib.util.module_from_spec(spec); spec.loader.exec_module(source)
CATEGORIES = source.CATEGORIES
score = source.score
native = source.native
reduce_j1 = source.reduce_j1


def merge_selected(baseline, rows):
    if any(not row["score"]["available"] for row in rows):
        return {"status": "null", "available": False, "valid": False, "labels": None}
    if any(not row["score"]["complete_map"] for row in rows):
        return {"status": "observed_invalid", "available": True, "valid": False, "labels": None}
    labels = dict(baseline)
    selected = set()
    for row in rows:
        new = row["score"]["labels"]
        if selected.intersection(new): raise ValueError("duplicate selected ID across recheck batches")
        selected.update(new); labels.update(new)
    return {"status": "valid", "available": True, "valid": True, "labels": labels}
