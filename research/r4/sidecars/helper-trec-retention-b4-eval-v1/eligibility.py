"""Reuse the fully authenticated c32/RL8/SFT8 endpoint qualification."""

import hashlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "helper-agnews-fresh512-eval-v1/eligibility.py"
EXPECTED = "b62864f9331f4794a4940ec8cc08460a64688c9ab16cede568f251c826bc68c8"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("qualified eligibility source changed")
text = raw.decode()
text = text.replace('path = study.ROOT / "ENDPOINTS_FIXED.json"', 'path = study.SOURCE_EVAL / "ENDPOINTS_FIXED.json"')
exec(compile(text, str(SOURCE), "exec"), globals())

