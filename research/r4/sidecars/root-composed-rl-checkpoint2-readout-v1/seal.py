import time
import readout_study as study
def build_ready(created_epoch=None):
    campaign=study.read(study.ROOT/"CAMPAIGN.json");decision=study.checkpoint2_decision()
    if not decision["run"]:raise ValueError("cannot seal readout before authenticated checkpoint2")
    return {"schema":"root-composed-rl-checkpoint2-readout-ready-v1",
           "created_epoch":time.time() if created_epoch is None else created_epoch,"identity":campaign["identity"],
           "campaign_sha256":study.sha(study.ROOT/"CAMPAIGN.json"),"checkpoint2":{"policy":decision["policy"],"owner_terminal_sha256":decision["owner_terminal_sha256"],"state_sha256":decision["state_sha256"]},
           "attempt":str(study.ATTEMPT),"gpu_launched":False}
if __name__=="__main__":
    ready=build_ready()
    study.write(study.ROOT/"READY.json",ready)
    print(ready["identity"])
