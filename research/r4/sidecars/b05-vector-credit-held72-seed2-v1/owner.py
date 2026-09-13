import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v4/owner.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="ab40f6482af2f95742df6cfbf0ecbf6eb362835d743420eb641d542bb31972e9";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
