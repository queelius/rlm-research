import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v4/collect.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="7b653791f8ffdffd0da3c35575bca5968e4740b4a8424775cce6f30c44ace566";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
