"""Seal V4 with the native launcher's mandatory fixed-selection receipt."""
import hashlib,types
from pathlib import Path
import study
selection={"schema":"b05-vector-credit-paired-checkpoint-qualification-v1","selection":"both fixed sole step1; no accuracy selection","local":study.endpoint(study.LOCAL),"joint":study.endpoint(study.JOINT),"outcomes_consulted":False}
study.write_x(study.ROOT/"CHECKPOINT_QUALIFICATION.json",selection)
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/prepare.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="523769008445912bd6e4c191d163c24044cddc44d7ba33b8c83a9c497188de05"
text=SOURCE.read_text();old='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]'
failed=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v3"
extras=[study.ROOT/"CHECKPOINT_QUALIFICATION.json",failed/"READY.json",failed/"outputs/attempt-001/OWNER_TERMINAL.json",failed/"outputs/attempt-001/RESULT.json",failed/"outputs/attempt-001/service/launcher.log"]
new='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]+[Path(x) for x in '+repr([str(p) for p in extras])+']';assert text.count(old)==1;text=text.replace(old,new)
assert text.count('"b05-vector-credit-held72-ready-v1"')==1;text=text.replace('"b05-vector-credit-held72-ready-v1"','"b05-vector-credit-held72-ready-v4"')
module=types.ModuleType("vector_credit_held_v4_prepare");module.__file__=str(SOURCE);module.__dict__["Path"]=Path;exec(compile(text,str(SOURCE),"exec"),module.__dict__)
if __name__=="__main__":module.main()
