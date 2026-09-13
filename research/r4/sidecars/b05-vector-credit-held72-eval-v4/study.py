"""Additive native selection-receipt binding repair over the unchanged V3 study."""
import hashlib
from pathlib import Path
SOURCE_STUDY=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v3/study.py"
assert hashlib.sha256(SOURCE_STUDY.read_bytes()).hexdigest()=="6f3b1df0a9f01a06d25f0389cd43c64e5b21d8013a3c44d98dea06e0c767bda4"
exec(compile(SOURCE_STUDY.read_text(),str(SOURCE_STUDY),"exec"),globals())
_binding_without_receipt=binding
def binding():
    value=_binding_without_receipt();path=ROOT/"CHECKPOINT_QUALIFICATION.json";receipt=read(path)
    assert receipt["selection"]=="both fixed sole step1; no accuracy selection"
    assert receipt["local"]["eligible"] and receipt["joint"]["eligible"]
    return {**value,"selection_path":str(path),"selection_sha256":sha(path)}
