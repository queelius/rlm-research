import time
import diagnostic_study as study
def prepare():
    root=study.ROOT
    sources=[p for p in sorted(root.glob("*.py")) if p.name not in {"prepare.py","seal.py"}]+[root/"DESIGN.md",root/"PLAN.md"]
    inputs=[study.GROUP,study.GENERATION,study.CHECKPOINT/"state.json",
            study.FAILURE_QUALIFICATION,study.SPARSE/"outputs/attempt-001/OWNER_TERMINAL.json",
            study.SPARSE/"READY.json",study.SPARSE/"CAMPAIGN.json"]
    campaign={"schema":"sparse-head-gradient-numerical-diagnostic-campaign-v1",
              "created_epoch":time.time(),"optimizer_authorized":False,"optimizer_steps":0,
              "passes":["dense_a","dense_b","sparse"],"work_cap_seconds":270,
              "outer_cap_seconds":300,"original_tolerances_unchanged":True,
              "source_sha256":{str(p):study.sha(p) for p in sources},
              "input_sha256":{str(p):study.sha(p) for p in inputs}}
    campaign["identity"]=study.digest(campaign);study.write(root/"CAMPAIGN.json",campaign);return campaign
if __name__=="__main__":print(prepare()["identity"])
