"""Prepare immutable inputs and scientific READY; no model calls."""
import json,time
from pathlib import Path
import checkpoint,study
DATA_SHA="3ff63cf269efaa8e3f9407722cf7c88714f95abf17eca5d2d701e399ab8c1861"
PARENT_SHA="d896540268ec2ced54414415de07db2e30c0d7c756a741487cd2165194efbd62"
def verify_receipt(path,expected):
    if study.sha(path)!=expected:raise ValueError("receipt changed: "+str(path))
    v=study.read(path)
    if v["identity"]!=study.digest({k:x for k,x in v.items() if k!="identity"}):raise ValueError("identity changed")
    for p,h in v["closure_sha256"].items():
        if study.sha(Path(p))!=h:raise ValueError("closure changed: "+p)
    return v
def build():
    if study.READY.exists() or any(path.exists() for path in (study.ROOT/"outputs/base-001",study.ROOT/"outputs/checkpoint32-001")):raise ValueError("unused ready/outputs required")
    data=verify_receipt(study.DATA/"DATA_READY.json",DATA_SHA);parent=verify_receipt(study.PARENT/"READY_V2.json",PARENT_SHA)
    cp=checkpoint.verify_checkpoint();prepared=study.prepare_inputs()
    if prepared!={"records":16,"episodes":16,"contexts":16,"prefixes":16,"schedule_sha256":study.digest(study.schedule())}:raise ValueError("prepared inventory differs")
    files=[study.ROOT/n for n in ("QUESTION.md","RUNBOOK.md","study.py","checkpoint.py","collect.py","owner.py","prepare.py","seal.py","test_eval.py")]
    files+=sorted(p for p in study.INPUTS.rglob("*") if p.is_file())
    closure={**data["closure_sha256"],**parent["closure_sha256"],str(study.DATA/"DATA_READY.json"):DATA_SHA,str(study.PARENT/"READY_V2.json"):PARENT_SHA,str(checkpoint.RECEIPT):study.sha(checkpoint.RECEIPT),**{str(p):study.sha(p) for p in files}}
    ready={"schema":"openai-mrcr-fourneedle-ordinal-transfer-eval-ready-v1","created_epoch":time.time(),"question":"Does procedural checkpoint32 transfer from first/second to third/fourth occurrence requests?","phase":"long","arms":["base","checkpoint32"],"outputs":{"base":str(study.ROOT/"outputs/base-001"),"checkpoint32":str(study.ROOT/"outputs/checkpoint32-001")},"inputs":{"records":16,"third_occurrence":8,"fourth_occurrence":8,"schedule_sha256":study.digest(study.schedule()),"seeds":list(range(202609260000,202609260016)),"data_ready_sha256":DATA_SHA,"gold_in_model_input":False},"sampling":{"temperature":.5,"top_p":1.,"top_k":-1,"min_p":0.,"max_tokens_per_action":2048,"max_total_root_child_turns":6},"checkpoint":{"fixed_primary_step":cp["fixed_primary_step"],"receipt":str(checkpoint.RECEIPT),"receipt_sha256":study.sha(checkpoint.RECEIPT),"checkpoint_selection":False,"child":"unchanged fixed zero-LoRA binding; actual calls measured"},"terminal_condition":parent["terminal_condition"],"metrics":{"primary":"raw exact","secondary":"official MRCR similarity","unavailable_not_wrong":True},"caps_seconds":{"science":600,"owner":700,"external":800},"optimizer_steps":0,"model_queries_before_ready":0,"claim_boundary":"ordinal transfer within same task and short band; common framing and unknown pretraining remain","closure_sha256":closure};ready["identity"]=study.digest(ready);study.write_x(study.READY,ready);return ready
if __name__=="__main__":
    v=build();print(json.dumps({"identity":v["identity"],"sha256":study.sha(study.READY)},sort_keys=True))
