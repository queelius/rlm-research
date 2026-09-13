import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v3/owner.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="4e9931301d59c4b97bd0ec5edfdea3d8745c790ef5707333df0ce0ec13356f15";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
