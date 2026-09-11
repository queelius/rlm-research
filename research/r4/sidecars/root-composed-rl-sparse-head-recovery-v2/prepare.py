import time
from pathlib import Path
import torch
import recovery2_study as study

def metric(a,b):
    a=a.double();b=b.double();d=a-b;aa=float(a.dot(a));bb=float(b.dot(b));dd=float(d.dot(d));ab=float(a.dot(b))
    return {"difference_l2":dd**.5,"relative_l2":(dd/aa)**.5,"cosine":ab/(aa*bb)**.5}
def prepare():
    diag=study.DIAG if hasattr(study,"DIAG") else study.SIDE/"root-composed-rl-sparse-head-numerical-diagnostic-v1"
    out=diag/"outputs/attempt-001/measurement";result=study.read(out/"RESULT.json")
    a=torch.load(out/"gradient-dense_a.pt",map_location="cpu",weights_only=True);b=torch.load(out/"gradient-dense_b.pt",map_location="cpu",weights_only=True);s=torch.load(out/"gradient-sparse.pt",map_location="cpu",weights_only=True)
    repeat=metric(a,b);sparse=metric(a,s);thresholds={"gradient_relative_l2_max":.03,"gradient_cosine_min":.9995,"sparse_difference_vs_repeat_ratio_max":2.0}
    old=result["captures"];logdiff=max(abs(x-y) for x,y in zip(old["dense_a"]["hf_old_logprobs"],old["sparse"]["hf_old_logprobs"]));lossdiff=abs(old["dense_a"]["loss"]-old["sparse"]["loss"])
    passed=repeat["relative_l2"]<=.03 and sparse["relative_l2"]<=.03 and repeat["cosine"]>=.9995 and sparse["cosine"]>=.9995 and sparse["difference_l2"]<=2*repeat["difference_l2"] and logdiff<=.005 and lossdiff<=.002
    artifacts=[out/"RESULT.json",out/"gradient-dense_a.pt",out/"gradient-dense_b.pt",out/"gradient-sparse.pt",diag/"outputs/attempt-001/OWNER_TERMINAL.json",study.V1/"outputs/attempt-001/qualification/QUALIFICATION_RESULT.json",study.V1/"READY.json"]
    req={"schema":"sparse-head-post-diagnostic-engineering-requalification-v1","created_epoch":time.time(),"passed":passed,"optimizer_steps":0,"dense_repeat":repeat,"dense_sparse":sparse,"max_action_logprob_difference":logdiff,"loss_difference":lossdiff,"post_diagnostic_engineering_thresholds":thresholds,"original_gate_remains_failed":True,"longest_sparse_finite_reused":True,"artifact_sha256":{str(p):study.sha(p) for p in artifacts}};req["identity"]=study.digest(req);study.write(study.ROOT/"REQUALIFICATION.json",req)
    sources=[p for p in sorted(study.ROOT.glob("*.py")) if p.name not in {"prepare.py","seal.py"}]+[study.ROOT/"DESIGN.md",study.ROOT/"PLAN.md"]
    inputs=[study.ROOT/"REQUALIFICATION.json",study.GROUP,study.GENERATION,study.CHECKPOINT/"state.json",study.V1/"CAMPAIGN.json",study.V1/"READY.json"]
    campaign={"schema":"sparse-head-update2-recovery-v2-campaign","created_epoch":time.time(),"question":"can exact update2 execute under explicit post-diagnostic engineering acceptance","source_sha256":{str(p):study.sha(p) for p in sources},"input_sha256":{str(p):study.sha(p) for p in inputs},"work_cap_seconds":1800,"optimizer_start":1,"target_optimizer_step":2};campaign["identity"]=study.digest(campaign);study.write(study.ROOT/"CAMPAIGN.json",campaign);return campaign
if __name__=="__main__":print(prepare()["identity"])
