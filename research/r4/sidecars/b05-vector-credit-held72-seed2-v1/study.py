"""Fresh-seed replication of the fixed held12 base/local/joint readout."""
import functools,hashlib
from pathlib import Path
SOURCE_STUDY=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v4/study.py";assert hashlib.sha256(SOURCE_STUDY.read_bytes()).hexdigest()=="80eac90f444d69e4ee57fe852f3173d3b76f987ff97732db7434168d5377c780"
exec(compile(SOURCE_STUDY.read_text(),str(SOURCE_STUDY),"exec"),globals())
@functools.lru_cache(None)
def calls():
    result=[]
    for index,task_row in enumerate(tasks()):
      for repeat in range(2):
        seed=202609520000+2*index+repeat;base={"arm":"vector","check_revisions":task_row["check_revisions"],"history_depth":task_row["history_depth"],"kind":"selection","max_tokens":384,"repeat":repeat,"root_id":task_row["root_id"],"seed":seed,"width":task_row["width"],"split":"held"}
        order=ARMS[(2*index+repeat)%3:]+ARMS[:(2*index+repeat)%3]
        for arm in order:result.append({**base,"arm":arm})
    return result
def verify():
    ready=read(READY);assert ready["identity"]==digest({k:v for k,v in ready.items() if k!="identity"})
    for path,want in ready["closure_sha256"].items():assert sha(path)==want,path
    assert len(tasks())==12 and len(calls())==72 and len({call_id(c) for c in calls()})==72
    assert sorted({c["seed"] for c in calls()})==list(range(202609520000,202609520024))
    schedule=read(ROOT/"SCHEDULE.json");assert schedule=={"schema":"b05-vector-credit-held72-seed2-schedule-v1","calls":[{"call":c,"prompt":prompt(c),"request":request_for(c)} for c in calls()]}
    assert all(len(request_for(c)["token_ids"])+384<=8192 for c in calls()) and binding()==read(ROOT/"BINDING.json");dependencies();return ready
