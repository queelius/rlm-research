import time
import recovery2_study as study
if __name__=="__main__":
 c=study.read(study.ROOT/"CAMPAIGN.json");r={"schema":"sparse-head-update2-recovery-v2-ready","created_epoch":time.time(),"identity":c["identity"],"campaign_sha256":study.sha(study.ROOT/"CAMPAIGN.json"),"attempt":str(study.ATTEMPT),"gpu_launched":False};study.write(study.ROOT/"READY.json",r);print(r["identity"])
