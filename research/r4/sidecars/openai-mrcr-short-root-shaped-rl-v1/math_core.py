"""Exact pinned root-trajectory math reused from the admitted MRCR preflight."""

import hashlib
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parent.parent
    / "mrcr-root-hf-one-update-preflight-v1/math_core.py"
)
EXPECTED = "13e2d36e3ad9c534dfe9f27570c30f6704184d55abee30321f7fc128620bf814"
raw = SOURCE.read_bytes()
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise ValueError("reviewed MRCR root math source changed")
exec(compile(raw, str(SOURCE), "exec"), globals())

