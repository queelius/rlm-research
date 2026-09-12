"""Own the fresh paired budgeted syntax-example screen on one native service."""

import hashlib
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "root-qs6-budgeted-evidence-stop-v1/owner.py"
SOURCE_SHA256 = "041bcd415378905a2581ff741f8df95ff97753e105b59a33b7c680974e1b3369"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
    raise ValueError("source owner changed")
text = SOURCE.read_text()
replacements = {
    "Own two sequential budgeted-evidence root screens on one service.": (
        "Own the fresh paired budgeted syntax-example root screen on one service."
    ),
    "qs6-budgeted-evidence-": "qs6-budgeted-syntax-",
    "exact unused budgeted-evidence attempt-001 required": (
        "exact unused budgeted-syntax attempt-001 required"
    ),
}
for before, after in replacements.items():
    if text.count(before) != 1:
        raise ValueError("source owner transform seam changed: " + before)
    text = text.replace(before, after)
exec(compile(text, str(SOURCE) + ":budgeted-syntax-screen", "exec"), globals())

