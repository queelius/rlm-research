"""Seal the fresh-seed schedule while reusing the qualified V4 stack."""
import hashlib,types
from pathlib import Path
import study
schedule={"schema":"b05-vector-credit-held72-seed2-schedule-v1","calls":[{"call":c,"prompt":study.prompt(c),"request":study.request_for(c)} for c in study.calls()]}
if (study.ROOT/"SCHEDULE.json").exists():assert study.read(study.ROOT/"SCHEDULE.json")==schedule
else:study.write_x(study.ROOT/"SCHEDULE.json",schedule)
selection={"schema":"b05-vector-credit-paired-checkpoint-qualification-v1","selection":"both fixed sole step1; no accuracy selection","local":study.endpoint(study.LOCAL),"joint":study.endpoint(study.JOINT),"outcomes_consulted":False}
if (study.ROOT/"CHECKPOINT_QUALIFICATION.json").exists():assert study.read(study.ROOT/"CHECKPOINT_QUALIFICATION.json")==selection
else:study.write_x(study.ROOT/"CHECKPOINT_QUALIFICATION.json",selection)
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v1/prepare.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="523769008445912bd6e4c191d163c24044cddc44d7ba33b8c83a9c497188de05"
text=SOURCE.read_text();old='[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]';successful=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v4"
extras=[study.ROOT/"CHECKPOINT_QUALIFICATION.json",study.ROOT/"SCHEDULE.json",successful/"READY.json",successful/"outputs/attempt-001/OWNER_TERMINAL.json",successful/"outputs/attempt-001/RESULT.json"]
new=old+'+[Path(x) for x in '+repr([str(path) for path in extras])+']';assert text.count(old)==1;text=text.replace(old,new)
assert text.count('"b05-vector-credit-held72-ready-v1"')==1;text=text.replace('"b05-vector-credit-held72-ready-v1"','"b05-vector-credit-held72-seed2-ready-v1"')
assert text.count('"source_schedule_sha256":study.sha(study.INPUTS)')==1;text=text.replace('"source_schedule_sha256":study.sha(study.INPUTS)','"source_schedule_sha256":study.sha(study.ROOT/"SCHEDULE.json")')
module=types.ModuleType("vector_credit_held_seed2_prepare");module.__file__=str(SOURCE);module.__dict__["Path"]=Path;exec(compile(text,str(SOURCE),"exec"),module.__dict__)
if __name__=="__main__":module.main()
