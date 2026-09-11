import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
V1=SIDE/"root-composed-rl-sparse-head-recovery-v1";DIAG=SIDE/"root-composed-rl-sparse-head-numerical-diagnostic-v1"
sys.path.insert(0,str(V1));import sparse_study as base  # noqa:E402
read=base.read;write=base.write;sha=base.sha;digest=base.digest;check=base.check
GROUP=base.GROUP;GENERATION=base.GENERATION;CHECKPOINT=base.CHECKPOINT;TRAIN=base.TRAIN
ATTEMPT=ROOT/"outputs/attempt-001"
def verify_requalification():
    value=read(ROOT/"REQUALIFICATION.json")
    for path,pin in value["artifact_sha256"].items():check(path,pin)
    if digest({k:v for k,v in value.items() if k!="identity"})!=value["identity"]:raise ValueError("requalification identity")
    if not value["passed"] or value["optimizer_steps"]!=0:raise ValueError("engineering requalification did not pass")
    return value
def verify_prepared():
    campaign=read(ROOT/"CAMPAIGN.json")
    if digest({k:v for k,v in campaign.items() if k!="identity"})!=campaign["identity"]:raise ValueError("campaign identity")
    for path,pin in {**campaign["source_sha256"],**campaign["input_sha256"]}.items():check(path,pin)
    verify_requalification();ready=read(ROOT/"READY.json")
    if ready["identity"]!=campaign["identity"] or ready["campaign_sha256"]!=sha(ROOT/"CAMPAIGN.json"):raise ValueError("READY identity")
    return campaign
