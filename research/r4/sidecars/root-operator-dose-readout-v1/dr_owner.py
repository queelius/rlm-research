"""Two serial fixed-checkpoint native phases within the additive6480s envelope."""
import argparse
import functools
import os
from pathlib import Path
import signal
import time
import traceback
import dr_study as s
class MainTermination(BaseException):pass

@functools.lru_cache(maxsize=1)
def dependencies():return s.dose.dependencies()
def remaining(deadline,cap):
    value=min(cap,deadline-time.time())
    if value<=0:raise TimeoutError('readout stage/shared deadline')
    return value
def check_output(output):
    if output.resolve()!=s.ATTEMPT.resolve():raise ValueError('exact new readout attempt')
    if output.exists():raise FileExistsError('no retry or overwrite')
def collector_argv(stage,destination,deadline):return [str(s.NATIVE),str(s.ROOT/'dr_collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','48','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]
def probe_argv(stage,destination,deadline):return [str(s.NATIVE),str(s.ROOT/'dr_probe.py'),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]

def training_receipt():
    terminal=s.dose.ATTEMPT/'OWNER_TERMINAL.json';owner=s.read(terminal)
    if not owner['complete'] or not owner['released']:raise ValueError('training must complete/release before readout; no partial24')
    selected={policy:s.selected(policy) for policy in ('sft6','sft24')};pins={str(terminal):s.sha(terminal)}
    for p in (s.dose.ATTEMPT/'training').glob('checkpoint-*/*'):
        if p.is_file():pins[str(p)]=s.sha(p)
    for name in ('RESULT.json','SELECTION.json','POST6_TEACHER_NLL.json','POST24_TEACHER_NLL.json','RESTORED_ADAM.json','RNG_RESTORED.json'):
        p=s.dose.ATTEMPT/'training'/name;pins[str(p)]=s.sha(p)
    return dict(selected=selected,actual_artifact_sha256=pins,training_ready_sha256=s.TRAIN_READY_SHA,training_elapsed_seconds=owner['elapsed_seconds'],training_outer_cap=4320,readout_outer_cap=6480,combined_reserved_seconds=10800,actual24_authenticated_before_service=True)

def usage(records):
    totals={k:0 for k in ('input','output','cached')};unknown={k:0 for k in totals}
    for record in records:
        raw=record.get('response') or {};u=raw.get('usage') if isinstance(raw,dict) else None
        if u is None:u=record.get('usage') or {}
        values=dict(input=u.get('prompt_tokens'),output=u.get('completion_tokens'),cached=(u.get('prompt_tokens_details') or {}).get('cached_tokens'))
        for k,v in values.items():
            if type(v)==int and v>=0:totals[k]+=v
            else:unknown[k]+=1
    return dict(known=totals,unknown=unknown)

def ledger(output):
    free_paths=sorted(output.glob('*/free/*/physical/*.json'));free=[s.read(p) for p in free_paths];attempts=[r for r in free if r.get('physical_request_attempt')]
    probe_paths=sorted(output.glob('*/probes/*/RESULT.json'));probes=[s.read(p) for p in probe_paths];probe_attempts=[r for r in probes if r.get('physical_request_attempt')]
    def returned(r):return isinstance(r.get('response'),dict) and bool(r['response'].get('choices'))
    return dict(full_native=dict(physical_requests_attempted=len(attempts),returned_native_completions=sum(returned(r) for r in attempts),failed_or_unconfirmed_completions=sum(not returned(r) for r in attempts),usage=usage(attempts)),first_action=dict(physical_requests_attempted=len(probe_attempts),http_responses_returned=sum(r.get('response_returned',False) for r in probe_attempts),authenticated_completions=sum(r.get('available',False) for r in probe_attempts),usage=usage(probe_attempts)),records_sha256={str(p):s.sha(p) for p in free_paths+probe_paths},training_and_historical_acquisition_not_counted_as_new_eval=True,billing='unknown/not measured',attempts_are_not_all_confirmed_GPU_generations=True)

def execute(output):
    started=time.time();work=started+6300;owned=started+6450;check_output(output);ready=s.verify();s.runtime();receipt=training_receipt()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns one GPU')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json')
    s.write(output/'PLANNED_EVALUATION.json',plan);s.write(output/'TRAINING_ARTIFACT_RECEIPT.json',receipt)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=6480,combined_training_readout_outer=10800,policy_order=plan['policy_order'],same_root_role=True,model_action_tokens=2048,context_tokens=8192,gpu=gpu,no_training=True))
    def expired(sig,frame):
        if sig in (signal.SIGINT,signal.SIGTERM):raise MainTermination('MAIN termination; no later phase')
        raise TimeoutError('inclusive readout cap')
    handlers={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()));errors=[];stages=[];active=None;halt=False
    try:
        for index,policy in enumerate(plan['policy_order']):
            if halt:break
            end=min(time.time()+3000,work-300-3000*(1-index));stage=output/('service-'+policy);stage.mkdir();status=dict(policy=policy,started_epoch=time.time(),deadline_epoch=end);active=stage
            try:
                startup=time.time()+remaining(end-90,180);signal.setitimer(signal.ITIMER_REAL,remaining(startup,180))
                suite.start_service(stage,s.binding(policy),startup)
                probe_end=time.time()+remaining(end-90,240);signal.setitimer(signal.ITIMER_REAL,remaining(probe_end,240))
                try:suite.command(stage,'first-action12',probe_argv(stage,output/policy/'probes',probe_end),remaining(probe_end,240),probe_end)
                except Exception as error:
                    # A diagnostic failure never gates otherwise runnable primary free coordinates.
                    status['probe_error']=dict(type=type(error).__name__,message=str(error));errors.append(dict(policy=policy,stage='probe',**status['probe_error']))
                collection=time.time()+remaining(end-90,2490);signal.setitimer(signal.ITIMER_REAL,remaining(collection,2490))
                suite.command(stage,'free48',collector_argv(stage,output/policy/'free',collection),remaining(collection,2490),collection)
                status['work_complete']=True
            except BaseException as error:
                status['error']=dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc());errors.append(dict(policy=policy,**status['error']))
                if not isinstance(error,Exception):halt=True
            finally:
                signal.setitimer(signal.ITIMER_REAL,max(.001,min(owned,time.time()+90)-time.time()))
                try:suite.release_service(stage);active=None
                except BaseException as error:status['release_error']=dict(type=type(error).__name__,message=str(error));errors.append(status['release_error']);halt=True
                status['ended_epoch']=time.time();stages.append(status);s.write(stage/'PHASE_TERMINAL.json',status);signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()))
    finally:
        # Harvest within the owned envelope even if a model phase exhausted work.
        full=[];probes=[]
        for row in plan['full']:
            path=output/row['policy']/'free'/row['coordinate']['id']/'RESULT.json';value=dict(row,result_path=str(path),recorded=False,operational_success=0,cause='unrun_or_interrupted')
            if path.exists():
                r=s.read(path);value.update(recorded=True,available=r['available'],reward=r['reward'],operational_success=int(r['available'] and r['reward']==1),result_sha256=s.sha(path),cause='native_final' if r['available'] else 'native_no_final_see_retained_trace')
            full.append(value)
        for row in plan['first_action']:
            path=output/row['policy']/'probes'/row['coordinate']['id']/'RESULT.json';value=dict(row,result_path=str(path),recorded=False)
            if path.exists():
                r=s.read(path);value.update(recorded=True,available=r['available'],result_sha256=s.sha(path))
            probes.append(value)
        s.write(output/'COST_LEDGER.json',ledger(output))
        result=dict(identity=ready['identity'],complete=not errors and len(stages)==2,error=errors or None,stages=stages,readout_inventory=full,first_action_inventory=probes,planned_full=96,planned_first_action=24,released=active is None,active_unreleased_service=str(active) if active else None,elapsed_seconds=time.time()-started,native_availability_not_implied_by_orchestrator_completion=True,no_partial24_substitution=True,no_training=True)
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    return result

def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ATTEMPT);return p.parse_args(argv)
if __name__=='__main__':
    a=parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        r=execute(a.output);print(dict(complete=r['complete'],errors=r['error'],elapsed_seconds=r['elapsed_seconds']));raise SystemExit(0 if r['complete'] else 1)
