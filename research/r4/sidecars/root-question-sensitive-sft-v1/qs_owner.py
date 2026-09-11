"""8100s owned pipeline with exact160 preinventory and protected144 reserve."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import qs_study as s
import qs_binding as b
class MainTermination(BaseException):pass
@functools.lru_cache(maxsize=1)
def dependencies():return s.cf.dose.dependencies()
def remaining(deadline):
    value=deadline-time.time()
    if value<=0:raise TimeoutError('question-sensitive shared/stage cap')
    return value
def stage_end(name,now,work):
    cap,reserve={'capture':(1200,6720),'training':(2100,4620),'unchanged':(2100,2520),'sft6':(2100,420)}[name]
    return min(now+cap,work-reserve)
def alarm(deadline):signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
def inventory(output):
    return [dict(row,path=str(output/row['policy']/('dev' if row['panel']=='dev' else 'free')/row['coordinate']['id']/'RESULT.json'),recorded=False,cause='not_started_no_artifacts',operational_success=0) for row in s.read(s.ROOT/'inputs/EVALUATION_PLAN.json')['full']]
def collector_argv(stage,destination,deadline,mode,plan,stop):return [str(s.NATIVE),str(s.ROOT/'qs_collect.py'),'--mode',mode,'--plan',plan,'--start','0','--stop',str(stop),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]
def error(caught):return dict(type=type(caught).__name__,message=str(caught),traceback=traceback.format_exc())
def ledger(output):
    old=s.load('qs_qualified_raw_union',s.CT/'ct_owner.py',s.ss.ct_ready['source_sha256'][str(s.CT/'ct_owner.py')],{'ct_study':s.ss.ct})
    paths=sorted(output.glob('**/physical/*.json'));records=[(p,s.read(p)) for p in paths]
    def tally(rows):
        attempted=[r for r in rows if r.get('physical_request_attempt')];returned=lambda r:isinstance(r.get('response'),dict) and bool(r['response'].get('choices'))
        return dict(physical_requests_attempted=len(attempted),http_responses_returned=sum(isinstance(r.get('response'),dict) or type(r.get('status'))==int for r in attempted),returned_native_completions=sum(returned(r) for r in attempted),failed_or_unconfirmed_completions=sum(not returned(r) for r in attempted),usage=old.usage(attempted))
    groups={'capture':[],'development':[],'protected':[],'other':[]}
    for path,row in records:
        parts=path.relative_to(output).parts;kind='capture' if parts[0]=='capture' else 'development' if len(parts)>1 and parts[1]=='dev' else 'protected' if len(parts)>1 and parts[1]=='free' else 'other';groups[kind].append(row)
    training=output/'training/RESULT.json'
    return dict(full_native=tally([r for p,r in records]),by_stage={k:tally(v) for k,v in groups.items()},authored_transport_records_not_model_calls=sum(r.get('origin','').startswith('authored') for p,r in records),records_sha256={str(p):s.sha(p) for p in paths},training_result_path=str(training),training_result_sha256=s.sha(training) if training.exists() else None,billing='unknown/not measured',attempts_are_not_all_confirmed_GPU_generations=True,scope='capture plus160 readout physical union; authored transport excluded from model work')
def harvest(output,planned):
    for row in planned:
        path=Path(row['path']);directory=path.parent;physical=list((directory/'physical').glob('*.json'));failure=directory/'FAILURE.json'
        if path.exists():
            value=s.read(path);row.update(recorded=True,available=value['available'],reward=value['reward'],operational_success=int(value['available'] and value['reward']==1),result_sha256=s.sha(path),cause='native_final' if value['available'] else 'attempted_native_no_final')
        elif failure.exists() or physical:row.update(cause='attempted_exception_no_result' if failure.exists() else 'attempted_interrupted_no_result',physical_records=len(physical),failure_sha256=s.sha(failure) if failure.exists() else None)
        elif directory.exists():row['cause']='started_no_physical_receipt'
    return planned
def execute(output):
    started=time.time();work=started+7920;owned=started+8070
    if output.resolve()!=s.ATTEMPT.resolve() or output.exists():raise ValueError('exact unused new attempt; no retry')
    s.runtime();ready=s.verify();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('one MAIN GPU/private credential preflight')
    output.mkdir(parents=True);suite=dependencies();planned=inventory(output);s.write(output/'PLANNED_EVALUATION.json',planned);s.write(output/'PLANNED_CAPTURE.json',[dict(coordinate=r,teacher=None) for r in s.read(s.ROOT/'inputs/TRAIN_PLAN.json')])
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=8100,phase_order=['unchanged','sft6'],stage_caps=dict(capture=1200,training=2100,dev_total=300,protected_total=3900,finalize=420),readout_service_allocation='each phase:150 dev plus1950 protected including startup/release',cleanup_seconds=150,outer_margin=30,model_action_tokens=2048,context_tokens=8192,credential_present=True,credential_value_logged=False,gpu=gpu))
    def expired(sig,frame):
        if sig in (signal.SIGTERM,signal.SIGINT):raise MainTermination('MAIN termination: no later phase')
        raise TimeoutError('active/shared cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM)};active=None;terminate=False;errors=[];stages=[];capture_ok=False
    def service(name,arm,end,body):
        nonlocal active,terminate
        stage=output/name;stage.mkdir();active=stage;status=dict(stage=name,started_epoch=time.time(),deadline_epoch=end)
        try:
            startup=min(time.time()+180,end-90);remaining(startup);alarm(startup);suite.start_service(stage,b.binding(arm),startup)
            body(stage,end-90,status);status['work_complete']=True
        except BaseException as caught:
            status['error']=error(caught);errors.append(dict(stage=name,**status['error']))
            if isinstance(caught,MainTermination) or not isinstance(caught,Exception):terminate=True
        finally:
            alarm(min(owned,end,time.time()+90))
            try:suite.release_service(stage);active=None
            except BaseException as caught:status['release_error']=error(caught);errors.append(dict(stage=name,**status['release_error']));terminate=True
            status['ended_epoch']=time.time();s.write(stage/'PHASE_TERMINAL.json',status);stages.append(status);alarm(owned)
        return status.get('work_complete',False) and active is None
    try:
        def capture(stage,end,status):
            remaining(end);alarm(end);suite.command(stage,'capture72',collector_argv(stage,output/'capture',end,'capture','TRAIN_PLAN.json',72),remaining(end),end);s.corpus()
        capture_ok=service('teacher-service','unchanged',stage_end('capture',time.time(),work),capture)
        if capture_ok and not terminate:
            end=stage_end('training',time.time(),work);stage=output/'train-stage';stage.mkdir();status=dict(stage='training',started_epoch=time.time(),deadline_epoch=end)
            try:
                remaining(end);alarm(end);argv=[str(s.TRAIN),str(s.ROOT/'qs_train.py'),'--mode','train','--output',str(output/'training'),'--deadline',str(float(end))]
                suite.command(stage,'gate-and-six-updates',argv,remaining(end),end);b.selected('sft6');status['work_complete']=True
            except BaseException as caught:
                status['error']=error(caught);errors.append(dict(stage='training',**status['error']))
                if isinstance(caught,MainTermination) or not isinstance(caught,Exception):terminate=True
            finally:status['ended_epoch']=time.time();s.write(stage/'PHASE_TERMINAL.json',status);stages.append(status);alarm(owned)
        for arm in ('unchanged','sft6'):
            if terminate or active is not None:break
            try:b.selected(arm)
            except Exception as caught:errors.append(dict(stage=arm,planned_fixed_policy_unavailable=True,**error(caught)));continue
            def readout(stage,end,status,arm=arm):
                dev_start=time.time();dev_end=min(dev_start+150,end)
                try:
                    remaining(dev_end);alarm(dev_end);suite.command(stage,'dev8',collector_argv(stage,output/arm/'dev',dev_end,'free','DEV_PLAN.json',8),remaining(dev_end),dev_end)
                except Exception as caught:errors.append(dict(stage=arm+'-dev',**error(caught)))
                dev_elapsed=time.time()-dev_start;status['dev_elapsed_seconds']=dev_elapsed
                # Protected1950 includes this phase's actual startup and reserved90 release;
                # dev wall is the sole excluded interval. Unused dev cap is not hidden free time.
                protected_end=min(end,status['started_epoch']+1950+dev_elapsed-90)
                status['protected_collection_deadline_epoch']=protected_end;remaining(protected_end);alarm(protected_end)
                suite.command(stage,'protected72',collector_argv(stage,output/arm/'free',protected_end,'free','FREE_PLAN.json',72),remaining(protected_end),protected_end)
            service('service-'+arm,arm,stage_end(arm,time.time(),work),readout)
    finally:
        alarm(min(owned,time.time()+420));rows=harvest(output,planned);s.write(output/'COST_LEDGER.json',ledger(output))
        result=dict(identity=ready['identity'],complete=not errors and all(r['recorded'] for r in rows),error=errors or None,readout_inventory=rows,planned_full=160,planned_protected=144,planned_dev=16,capture_complete=capture_ok,stages=stages,released=active is None,active_unreleased_service=str(active) if active else None,elapsed_seconds=time.time()-started,no_retry=True,no_partial_fixed6_substitution=True,orchestrator_complete_not_native_availability=True)
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return result
def parse_args():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run','verify'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);return ap.parse_args()
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],error=result['error']));raise SystemExit(0 if result['complete'] else 1)
