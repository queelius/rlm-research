"""Seal V3 by exact transformation of the immutable V2 sealer."""
import hashlib, types
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-shared-v2/prepare_arm.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="b7a42b5605fd3468d2758b92ce4762f9d9aa038ef22c86c494981e267321b5df"
text=SOURCE.read_text()
old='("READY.json", "outputs/attempt-001/START.json", "outputs/attempt-001/RESULT.json")'
new='("READY.json", "outputs/attempt-001/OWNER_START.json", "outputs/attempt-001/OWNER_TERMINAL.json", "outputs/attempt-001/train.stdout", "outputs/attempt-001/train.stderr", "outputs/attempt-001/RESULT.json")'
assert text.count(old)==1;text=text.replace(old,new)
assert text.count('"b05-vector-credit-ready-v2"')==1
text=text.replace('"b05-vector-credit-ready-v2"','"b05-vector-credit-ready-v3"')
module=types.ModuleType("vector_credit_prepare_v3");module.__file__=str(SOURCE)
exec(compile(text,str(SOURCE),"exec"),module.__dict__)
prepare=module.prepare
