import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v4/metrics.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="84cdb28833d04d6e6bc634e580ef7c6e12a2932713b08b83117e5862889411ae";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
