"""Seal V3 and pin both earlier unlaunched evaluator failures."""
import hashlib,types
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/prepare.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="523769008445912bd6e4c191d163c24044cddc44d7ba33b8c83a9c497188de05"
text=SOURCE.read_text();old='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]'
failed=[Path(__file__).resolve().parents[1]/name/"READY.json" for name in ("b05-vector-credit-held72-eval-v1","b05-vector-credit-held72-eval-v2")]
new='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]+[Path(x) for x in '+repr([str(p) for p in failed])+']'
assert text.count(old)==1;text=text.replace(old,new);assert text.count('"b05-vector-credit-held72-ready-v1"')==1;text=text.replace('"b05-vector-credit-held72-ready-v1"','"b05-vector-credit-held72-ready-v3"')
module=types.ModuleType("vector_credit_held_v3_prepare");module.__file__=str(SOURCE);module.__dict__["Path"]=Path;exec(compile(text,str(SOURCE),"exec"),module.__dict__)
if __name__=="__main__":module.main()
