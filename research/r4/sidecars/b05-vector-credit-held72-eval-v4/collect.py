import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v3/collect.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="3490a8a18d3e11199d942a0a3e537de63f8dd5b3b818415a72efc52880c398e8";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
