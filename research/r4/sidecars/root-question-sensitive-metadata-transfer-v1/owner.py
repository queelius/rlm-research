"""Two serial readout services, per-episode checkpoints, bounded release."""
import argparse
import os
from pathlib import Path
import signal
import time
import study as s
import qs_owner as qualified

def execute(output):
    output=Path(output);started=time.time();work=started+3750;owned=started+3870
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('unused fixed namespace')
    ready=s.verify();s.runtime()
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('assigned GPU/key required')
    output.mkdir(parents=True);suite=qualified.dependencies();plan=s.read(s.ROOT/'inputs/FREE_PLAN.json')
    planned=[dict(policy=arm,coordinate=row,path=str(output/arm/'free'/row['id']/'RESULT.json'),recorded=False)
             for arm in ('sft6','unchanged') for row in plan]
    s.write(output/'PLANNED.json',planned)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=3900,policy_order=['sft6','unchanged'],planned=144,no_training=True,no_retry=True))
    def expired(sig,frame):
        if sig in (signal.SIGINT,signal.SIGTERM):raise qualified.MainTermination('MAIN cancellation')
        raise TimeoutError('readout cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    errors=[];stages=[];active=None;terminate=False
    try:
        for arm in ('sft6','unchanged'):
            if terminate or active is not None:break
            stage=output/('service-'+arm);stage.mkdir();active=stage
            end=min(time.time()+1800,work);status=dict(policy=arm,started_epoch=time.time(),deadline_epoch=end)
            try:
                startup=min(time.time()+180,end-90);qualified.alarm(startup)
                suite.start_service(stage,s.binding(arm),startup)
                deadline=end-90;qualified.alarm(deadline)
                argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','72','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(output/arm/'free'),'--deadline',str(deadline)]
                suite.command(stage,'readout72',argv,qualified.remaining(deadline),deadline)
                status['work_complete']=True
            except BaseException as e:
                status['error']=qualified.error(e);errors.append(status['error'])
                if not isinstance(e,Exception):terminate=True
            finally:
                qualified.alarm(min(owned,time.time()+90))
                try:suite.release_service(stage);active=None
                except BaseException as e:errors.append(qualified.error(e));terminate=True
                status['ended_epoch']=time.time();s.write(stage/'PHASE_TERMINAL.json',status);stages.append(status)
    finally:
        qualified.alarm(min(owned,time.time()+90));rows=qualified.harvest(output,planned)
        s.write(output/'COST_LEDGER.json',qualified.ledger(output))
        result=dict(identity=ready['identity'],complete=not errors and all(r['recorded'] for r in rows),released=active is None,active_unreleased_service=str(active) if active else None,error=errors or None,stages=stages,inventory=rows,planned=144,elapsed_seconds=time.time()-started)
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ATTEMPT);a=p.parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(a.output);print(dict(complete=result['complete'],released=result['released']));raise SystemExit(0 if result['complete'] else 1)
