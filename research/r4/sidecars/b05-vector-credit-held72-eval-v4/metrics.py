import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v3/metrics.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="a1d8bc452528cb3b0937d9cbfe56fe0b6f597b9990f38778da74cb2e66e60463";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
