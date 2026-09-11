import argparse,os,signal,time
from pathlib import Path
import collect
import study as s
class MainTermination(BaseException):pass
def collector_argv(stage,output,deadline):return [str(s.NATIVE),str(s.ROOT/"collect.py"),"--endpoint",str(stage/"service/endpoint-original.json"),"--output",str(output),"--deadline",str(float(deadline))]
def execute(output):
 output=Path(output);started=time.time();work=started+1050;owned=started+1170
 if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError("exact unused attempt required")
 ready=s.verify();gpu=os.environ.get("CUDA_VISIBLE_DEVICES","");
 if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):raise ValueError("one MAIN GPU and credential required")
 suite=s.dependencies();plan=s.read(s.ROOT/"inputs/PLAN.json");output.mkdir(parents=True);stage=output/"owned-service";stage.mkdir();s.write(output/"PLANNED.json",plan);s.write(output/"OWNER_RUN.json",{"identity":ready["identity"],"started_epoch":started,"work_deadline":work,"owned_deadline":owned,"outer_seconds":1200,"planned_child_calls":40,"root_model_calls":0,"runtime_fallback":False,"gpu":gpu,"credential_present":True})
 def expired(sig,frame):
  if sig in (signal.SIGINT,signal.SIGTERM):raise MainTermination("MAIN cancellation")
  raise TimeoutError("bounded stats cap")
 hs={x:signal.signal(x,expired) for x in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};errors=[];active=True
 try:
  startup=min(work-30,time.time()+180);signal.setitimer(signal.ITIMER_REAL,max(.001,startup-time.time()));suite.start_service(stage,s.binding(),startup);signal.setitimer(signal.ITIMER_REAL,max(.001,work-time.time()));suite.command(stage,"j1-sufficient-statistics40",collector_argv(stage,output/"rollout",work),max(.001,work-time.time()),work)
 except BaseException as e:errors.append({"stage":"work","type":type(e).__name__,"message":str(e)})
 finally:
  release=time.time();signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned-30,time.time()+90)-time.time()))
  try:suite.release_service(stage);active=False
  except BaseException as e:errors.append({"stage":"release","type":type(e).__name__,"message":str(e)})
  signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()));m=collect.implementation();ledger=m.harvest(output/"rollout",plan);s.write(output/"COST_LEDGER.json",{k:v for k,v in ledger.items() if k!="rows"});result={"identity":ready["identity"],"complete":not errors,"released":not active,"active_unreleased_service":str(stage) if active else None,"error":errors or None,"inventory":ledger["rows"],"planned":40,"physical":ledger["cost"],"elapsed_seconds":time.time()-started,"release_started_epoch":release,"ended_epoch":time.time(),"root_model_calls":0,"no_training":True,"no_retry":True,"runtime_fallback":False};s.write(output/"OWNER_TERMINAL.json",result);signal.setitimer(signal.ITIMER_REAL,0)
  for sig,h in hs.items():signal.signal(sig,h)
 return result
def main():
 a=argparse.ArgumentParser();a.add_argument("command",choices=("verify","run"));a.add_argument("--output",type=Path,default=s.ATTEMPT);x=a.parse_args()
 if x.command=="verify":print(s.verify()["identity"])
 else:
  r=execute(x.output);print({"complete":r["complete"],"released":r["released"]});raise SystemExit(0 if r["complete"] else 1)
if __name__=="__main__":main()
