"""Pinned reviewed collector under the V3 study namespace."""
import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/collect.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="8a42eb0b349ba0f110c9739fccc5ed0170b40c13ce1e743c00bb50285a28d9ac"
exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
