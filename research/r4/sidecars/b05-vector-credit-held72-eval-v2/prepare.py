"""Additive seal preserving the unlaunched V1 import failure."""
import hashlib,types
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/prepare.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="523769008445912bd6e4c191d163c24044cddc44d7ba33b8c83a9c497188de05"
text=SOURCE.read_text();old='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]'
failed=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/READY.json"
new='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json",Path("'+str(failed)+'")]'
assert text.count(old)==1;text=text.replace(old,new)
assert text.count('"b05-vector-credit-held72-ready-v1"')==1;text=text.replace('"b05-vector-credit-held72-ready-v1"','"b05-vector-credit-held72-ready-v2"')
module=types.ModuleType("vector_credit_held_v2_prepare");module.__file__=str(SOURCE);module.__dict__["Path"]=Path
exec(compile(text,str(SOURCE),"exec"),module.__dict__)
if __name__=="__main__":module.main()
