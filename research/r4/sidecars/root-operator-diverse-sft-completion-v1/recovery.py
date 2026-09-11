"""Additive MAIN-only train+fixed6 completion; original corpus/baseline remain immutable."""
import argparse
import asyncio
import functools
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import types

ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'root-operator-diverse-sft-v1';ATTEMPT=ROOT/'outputs/attempt-001'
spec=importlib.util.spec_from_file_location('operator_completion_original_study',OLD/'od_study.py')
s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
if s.sha(OLD/'od_study.py')!='3d437ec69d3a1f0dfa038e5c7bbd7dcd770c512b39660385cc9a6759e29d2143':raise ValueError('original study changed')
ORIGINAL_READY_SHA='3ca5943ec51e8b45525bf4c9dfe4a50616517279aa057e76127d440deaab9dde'

@functools.lru_cache(maxsize=1)
def protocol():
    module=s.load('operator_completion_original_protocol',OLD/'od_protocol.py',s.read(OLD/'READY_v2.json')['source_sha256'][str(OLD/'od_protocol.py')],{'od_study':s})
    with s.aliases({'od_study':s}):module.shared()
    return module

@functools.lru_cache(maxsize=1)
def binding_module():
    path=OLD/'od_binding.py';source=path.read_text();pin=s.read(OLD/'READY_v2.json')['source_sha256'][str(path)]
    if s.sha(path)!=pin:raise ValueError('original binding changed')
    before="directory=s.ATTEMPT/'training';"
    if source.count(before)!=1:raise ValueError('exact one training directory adaptation')
    module=types.ModuleType('operator_completion_original_binding');module.__file__=str(path)
    module.RECOVERY_TRAINING=ATTEMPT/'training';sys.modules[module.__name__]=module
    with s.aliases({'od_study':s}):exec(compile(source.replace(before,'directory=RECOVERY_TRAINING;'),str(path)+'::new-training-directory-only','exec'),module.__dict__)
    return module

def selected():return binding_module().selected('sft6')

@functools.lru_cache(maxsize=1)
def collector():
    path=OLD/'od_collect.py'
    module=s.load('operator_completion_original_collector',path,s.read(OLD/'READY_v2.json')['source_sha256'][str(path)],{'od_study':s,'od_protocol':protocol()})
    with s.aliases({'od_study':s,'od_protocol':protocol(),'od_binding':binding_module()}):return module.implementation()

@functools.lru_cache(maxsize=1)
def dependencies():
    path=OLD/'od_owner.py'
    module=s.load('operator_completion_original_owner',path,s.read(OLD/'READY_v2.json')['source_sha256'][str(path)],{'od_study':s,'od_protocol':protocol(),'od_binding':binding_module()})
    return module.dependencies()

def verify():
    ready=s.read(ROOT/'READY.json')
    if s.digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('completion READY identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
        if s.sha(path)!=pin:raise ValueError('completion closure changed: '+path)
    if s.sha(OLD/'READY_v2.json')!=ORIGINAL_READY_SHA:raise ValueError('original acceptance changed')
    s.verify();s.corpus()
    return ready

def remaining(deadline):
    result=deadline-time.time()
    if result<=0:raise TimeoutError('completion shared/stage deadline')
    return result
def train_deadline(now,work):return min(now+3600,work-1500)
def alarm(deadline):signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
def check_output(output):
    if output.resolve()!=ATTEMPT.resolve():raise ValueError('exact new completion attempt only')
    if output.exists():raise FileExistsError('completion exists; no retry or overwrite')
def training_argv(output,deadline):return [str(s.TRAIN),str(OLD/'od_train.py'),'--mode','train','--output',str(output/'training'),'--deadline',str(float(deadline))]
def collector_argv(stage,destination,deadline):return [str(s.NATIVE),str(ROOT/'collect.py'),'--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','24','--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(destination),'--deadline',str(float(deadline))]
def inventory(output):return [dict(arm='sft6',coordinate=row,path=str(output/'sft6/free'/row['id']/'RESULT.json'),original_baseline_path=str(s.ATTEMPT/'unchanged/free'/row['id']/'RESULT.json'),available=False,reward=None,recorded=False,reason='planned fixed6 before training') for row in s.read(OLD/'inputs/FREE_PLAN.json')]
def exception(error):return dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc())

def gpu_command(suite,stage,argv,deadline):
    """Qualified joint-owned process pattern; only cap changes from600 to stage remainder."""
    stage.mkdir();cap=remaining(deadline)
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns exactly one GPU')
    s.write(stage/'COMMAND.json',dict(argv=argv,deadline_epoch=deadline,cap_seconds=cap,started_epoch=time.time(),gpu=gpu,gpu_visible_to_command=True))
    with (stage/'process.log').open('x') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        observed=suite.life.observe(process.pid)
        if observed is None:
            process.wait(timeout=5);s.write(stage/'EXIT.json',dict(returncode=process.returncode,already_exited=True,ended_epoch=time.time()))
            raise RuntimeError('train exited before owner observation')
        owner=suite.life.safe_observation(observed);s.write(stage/'PROCESS.json',owner)
        try:
            if process.wait(timeout=cap):raise RuntimeError('training nonzero; no retry or partial6')
        finally:suite.stop_child(process,owner);s.write(stage/'EXIT.json',dict(returncode=process.returncode,ended_epoch=time.time()))

class MainTermination(BaseException):pass

def execute(output):
    started=time.time();work=started+5220;owned=started+5370;check_output(output);ready=verify()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN assigns exactly one GPU')
    if not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('private credential required')
    suite=dependencies();output.mkdir(parents=True,exist_ok=False);planned=inventory(output)
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',planned)
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=started,work_deadline_epoch=work,owned_deadline_epoch=owned,outer_seconds=5400,cleanup_seconds=150,outer_margin_seconds=30,stage_caps=dict(training=3600,sft6_including_start_release=1200,finalization=300,slack=120),gpu=gpu,original_attempt=str(s.ATTEMPT),original_corpus_sha256=s.sha(s.ATTEMPT/'capture/CORPUS_READY.json'),original_scientific_identity=s.verify()['identity'],training_start='fresh Adam at zero; old process failed before load',baseline_rerun=False,capture_rerun=False,time_separated_recovery=True))
    def expired(sig,_frame):
        if sig in (signal.SIGINT,signal.SIGTERM):raise MainTermination('MAIN termination')
        raise TimeoutError('completion stage/owned deadline')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    stages=[];errors=[];active=None;terminated=False;fixed6=False;alarm(owned)
    try:
        deadline=train_deadline(time.time(),work);status=dict(stage='training',started_epoch=time.time(),deadline_epoch=deadline)
        try:
            alarm(deadline);gpu_command(suite,output/'train-stage',training_argv(output,deadline),deadline);selected();fixed6=True;status['work_complete']=True
        except BaseException as error:
            status['error']=exception(error);errors.append(dict(stage='training',**status['error']))
            if isinstance(error,MainTermination) or not isinstance(error,Exception):terminated=True
        finally:status['ended_epoch']=time.time();stages.append(status);s.write(output/'TRAIN_PHASE_TERMINAL.json',status);alarm(owned)
        if fixed6 and not terminated:
            deadline=min(time.time()+1200,work-300);stage=output/'service-sft6';stage.mkdir();active=stage;status=dict(stage='sft6',started_epoch=time.time(),deadline_epoch=deadline)
            try:
                startup=min(time.time()+180,deadline-90);remaining(startup);alarm(startup)
                suite.start_service(stage,binding_module().binding('sft6'),startup)
                collection=deadline-90;remaining(collection);alarm(collection)
                suite.command(stage,'fixed-sft6-24',collector_argv(stage,output/'sft6/free',collection),remaining(collection),collection)
                status['work_complete']=True
            except BaseException as error:status['error']=exception(error);errors.append(dict(stage='sft6',**status['error']))
            finally:
                alarm(min(owned,time.time()+90))
                try:suite.release_service(stage);active=None
                except BaseException as error:status['release_error']=exception(error);errors.append(dict(stage='release',**status['release_error']))
                status['ended_epoch']=time.time();stages.append(status);s.write(output/'READOUT_PHASE_TERMINAL.json',status);alarm(owned)
    finally:
        alarm(min(work,owned))
        for row in planned:
            path=Path(row['path'])
            if path.exists():
                value=s.read(path);row.update(recorded=True,available=value['available'],reward=value['reward'],reason=value.get('reason'),result_sha256=s.sha(path))
            else:row['reason']='fixed6 missing or endpoint unrun/incomplete; no substitution'
        paths=sorted(output.glob('**/physical/*.json'));records=[s.read(path) for path in paths];attempted=[x for x in records if x.get('physical_request_attempt')]
        s.write(output/'COST_LEDGER.json',dict(new_physical_requests_attempted=len(attempted),new_usage=protocol().physical_cost(attempted),new_record_sha256={str(path):s.sha(path) for path in paths},original_shared_ledger_path=str(s.ATTEMPT/'COST_LEDGER.json'),original_shared_ledger_sha256=s.sha(s.ATTEMPT/'COST_LEDGER.json'),capture_repeated=False,baseline_repeated=False,billing_unknown=True))
        result=dict(complete=not errors and fixed6 and all(x['recorded'] for x in planned),errors=errors,stages=stages,fixed6_available=fixed6,planned=24,readout_inventory=planned,active_unreleased_service=str(active) if active else None,elapsed_seconds=time.time()-started,original_attempt_unchanged=True,original_sft24_nulls_preserved=True,time_separated_recovery=True,orchestrator_completion_not_native_availability=True,no_partial_substitution=True)
        s.write(output/'OWNER_TERMINAL.json',result);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    return result

def parse_args(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--output',type=Path,default=ATTEMPT);return parser.parse_args(argv)
if __name__=='__main__':
    args=parse_args()
    if args.command=='verify':print(verify()['identity'])
    else:
        result=execute(args.output);print(dict(complete=result['complete'],elapsed_seconds=result['elapsed_seconds']));raise SystemExit(0 if result['complete'] else 1)
