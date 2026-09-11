"""Seal the conditional readout without consulting sparse recovery outcomes."""
from pathlib import Path
import readout_study as study

ROOT=study.ROOT

def prepare():
    sources=[p for p in sorted(ROOT.glob("*.py")) if p.name not in {"prepare.py","seal.py"}]
    sources += [ROOT/"DESIGN.md",ROOT/"PLAN.md"]
    inputs=[study.SOURCE/"inputs"/name for name in
            ("PLANS.json","PUBLIC.json","HOST_GOLD.json","TASKS.json","NATIVE_TEMPLATE.json")]
    inputs += [study.SOURCE/"READY.json",study.SOURCE/"CAMPAIGN.json",
               study.SPARSE/"READY.json",study.SPARSE/"CAMPAIGN.json"]
    campaign={"schema":"root-composed-rl-checkpoint2-readout-campaign-v1",
              "question":"behavior at fixed recovered Adam2 versus existing Adam1/start",
              "conditional":"zero-request skip unless exact sparse recovery commits step2",
              "planned_endpoints":72,"policies_new":["checkpoint2"],
              "comparators_reused":["start","checkpoint1"],
              "budget_seconds":{"work":2400,"owned":2670,"outer":2700},
              "source_sha256":{str(p):study.sha(p) for p in sources},
              "input_sha256":{str(p):study.sha(p) for p in inputs}}
    campaign["identity"]=study.digest(campaign)
    study.write(ROOT/"CAMPAIGN_V3.json",campaign)
    return campaign
if __name__=="__main__": print(prepare()["identity"])
