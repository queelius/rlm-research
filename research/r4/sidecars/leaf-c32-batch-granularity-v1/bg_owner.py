"""MAIN-only1050work/1170owned/1200outer owner; no retry or root inference."""
import argparse
import os
from pathlib import Path
import signal
import time
import bg_study as s
import bg_collect as c
class MainTermination(BaseException):pass
def collector_argv(stage,output,deadline):return [str(s.NATIVE),str(s.ROOT/'bg_collect.py'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(output),'--deadline',str(float(deadline))]
def execute(output):
    output=Path(output);started=time.time();work=started+1050;owned=started+1170
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused attempt required')
    ready=s.verify();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('one MAIN GPU and private credential required')
    suite=s.dependencies();plan=s.read(s.ROOT/'inputs/PLAN.json');output.mkdir(parents=True);stage=output/'owned-service';stage.mkdir()
    s.write(output/'PLANNED.json',plan);s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline=work,owned_deadline=owned,outer_seconds=1200,startup_cap=180,collector_harvest_reserve=30,release_cap=90,finalize_reserve=30,outer_margin=30,scientific_role='child_only',credential_present=True,gpu=gpu))
    def expired(sig,frame):
        if sig in (signal.SIGINT,signal.SIGTERM):raise MainTermination('MAIN cancellation')
        raise TimeoutError('bounded batch-granularity stage cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};errors=[];active=True
    try:
        startup=min(work-30,time.time()+180);signal.setitimer(signal.ITIMER_REAL,max(.001,startup-time.time()))
        suite.start_service(stage,s.binding(),startup)
        signal.setitimer(signal.ITIMER_REAL,max(.001,work-time.time()))
        suite.command(stage,'child76',collector_argv(stage,output/'rollout',work),max(.001,work-time.time()),work)
    except BaseException as error:errors.append(dict(stage='work',type=type(error).__name__,message=str(error)))
    finally:
        release_started=time.time();signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned-30,time.time()+90)-time.time()))
        try:suite.release_service(stage);active=False
        except BaseException as error:errors.append(dict(stage='release',type=type(error).__name__,message=str(error)))
        signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()))
        ledger=c.harvest(output/'rollout',plan);s.write(output/'COST_LEDGER.json',{k:v for k,v in ledger.items() if k!='rows'})
        public={x['id']:x for x in s.read(s.ROOT/'inputs/PUBLIC.json')};s.write(output/'SUMMARY.json',c.summarize(ledger['rows'],s.read(s.ROOT/'inputs/HOST_GOLD.json'),public))
        result=dict(identity=ready['identity'],complete=not errors,released=not active,active_unreleased_service=str(stage) if active else None,error=errors or None,inventory=ledger['rows'],planned=76,physical=ledger['cost'],elapsed_seconds=time.time()-started,release_started_epoch=release_started,ended_epoch=time.time(),root_model_calls=0,no_training=True,no_retry=True)
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);args=ap.parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],released=result['released']));raise SystemExit(0 if result['complete'] else 1)
if __name__=='__main__':main()
