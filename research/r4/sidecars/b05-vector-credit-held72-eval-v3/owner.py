"""Pinned finite owner under repaired V3 imports."""
import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/owner.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="4dcfe6717ab55968abe1fcba1919b9ffb683a0a679290a63c79be78ea21e0465"
exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
