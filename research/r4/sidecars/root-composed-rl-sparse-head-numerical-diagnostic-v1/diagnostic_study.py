import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
SPARSE=SIDE/"root-composed-rl-sparse-head-recovery-v1";ATTEMPT=ROOT/"outputs/attempt-001"
sys.path.insert(0,str(SPARSE));import sparse_study as base  # noqa:E402
read=base.read;write=base.write;sha=base.sha;digest=base.digest;check=base.check
GROUP=base.GROUP;GENERATION=base.GENERATION;CHECKPOINT=base.CHECKPOINT;TRAIN=base.TRAIN;SOURCE=base.SOURCE
FAILURE_QUALIFICATION=SPARSE/"outputs/attempt-001/qualification/QUALIFICATION_RESULT.json"
FAILURE_PIN=""  # populated by prepare.py and campaign verification
def verify_inputs():
    receipt=base.verify_inputs()
    campaign=read(ROOT/"CAMPAIGN.json")
    for path,pin in {**campaign["source_sha256"],**campaign["input_sha256"]}.items():check(path,pin)
    return receipt
def verify_prepared():
    c=read(ROOT/"CAMPAIGN.json")
    if digest({k:v for k,v in c.items() if k!="identity"})!=c["identity"]:raise ValueError("campaign identity")
    verify_inputs();r=read(ROOT/"READY.json")
    if r["identity"]!=c["identity"] or r["campaign_sha256"]!=sha(ROOT/"CAMPAIGN.json"):raise ValueError("READY identity")
    return c
