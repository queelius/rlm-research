"""Additive grader-interface repair; schedule and checkpoints remain unchanged."""
import hashlib
from pathlib import Path
SOURCE_STUDY=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/study.py"
assert hashlib.sha256(SOURCE_STUDY.read_bytes()).hexdigest()=="58c589b3f30641ce2ab956b695688c2a1a493149e544a9b2c8b640e90912713a"
exec(compile(SOURCE_STUDY.read_text(),str(SOURCE_STUDY),"exec"),globals())
