"""Main-invoked three-phase owned evaluation with shared absolute deadlines."""
import argparse
import asyncio
import fcntl
import json
import os
import sys
import time
from pathlib import Path
import experiment as e
import results

saved=sys.modules.get('study')
sys.modules['study']=e.old
sys.path.insert(0,str(e.old.ROOT))
inherited=e.checked_import('uptake_original_driver',e.old.ROOT/'driver.py','c2ff3561af4cee9f46a989f19dc2f9d6d3cc9f2c6ba3410fd1a5fc07b4e7d4b2')
sys.path.insert(0,str(e.ROOT))
if saved is None: sys.modules.pop('study',None)
else: sys.modules['study']=saved
inherited.s,inherited.analysis=e,results
c=e.c
OBSERVER_PATH=e.ROOT.parents[1]/'operations/2026-09-09-after-identity-receipt/receipt_driver.py'
OBSERVER_SHA='e2789bf5c4df114f8005f83dcfb68a909888995e2677c395a5d6de969b7a1c83'


def install_observer(coordinator):
    wrapper=e.checked_import('uptake_qualified_observer',OBSERVER_PATH,OBSERVER_SHA)
    wrapper.install_observer(coordinator)


def collection_cap(phase_cap,collection_spent,reserve_after,work_deadline,now):
    return min(phase_cap,2400-collection_spent,work_deadline-now-30-reserve_after)


async def collect(spec,output):
    previous=e.capture.base
    e.capture.base=e.collector()
    try: return await inherited.collect(spec,output)
    finally: e.capture.base=previous


def verify_ready():
    spec=e.verify()
    ready=c.read(e.ROOT/'READY.json')
    c.authenticate(ready['artifact_sha256'])
    if (ready['spec_sha256']!=c.file_hash(e.ROOT/'SPEC.json') or ready['planned']!=96
        or ready['driver_sha256']!=c.file_hash(Path(__file__))):
        raise ValueError('READY source/count changed')
    proof=c.read(e.ROOT/'qualification-attempt-002/RESULT.json')
    if proof['actual_model_calls']!=0 or proof['gpu_calls']!=0 or proof['conditions']!=list(e.ARMS):
        raise ValueError('CPU runtime proof missing')
    return spec


def run(output):
    started=time.time()
    deadline,work_deadline=started+3600,started+3480
    spec=verify_ready()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('main must assign GPU and existing credential')
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    c.write_once(output/'RUN.json',{'started_epoch':started,'deadline_epoch':deadline,'work_deadline_epoch':work_deadline,
        'spec_sha256':c.file_hash(e.ROOT/'SPEC.json'),'ready_sha256':c.file_hash(e.ROOT/'READY.json'),'gpu':gpu,
        'phase_order':list(e.PHASES),'collection_cap_seconds':2400})
    life,coordinator=inherited.lifecycle,inherited.coordinator
    install_observer(coordinator)
    life.install()
    e.native.binding_for=e.binding_for
    error,statuses=None,[]
    collection_spent=0
    try:
        for phase_name in e.PHASES:
            if work_deadline-time.time()<180: raise TimeoutError('shared deadline lacks startup/collection margin')
            weight=e.PHASE_WEIGHTS[phase_name]
            service_dir=output/'services'/phase_name
            binding,endpoint=coordinator.start_service(service_dir,spec['policies'][weight],work_deadline)
            try:
                phase=output/('phase-'+phase_name)
                phase.mkdir()
                cap=collection_cap(e.PHASE_CAPS[phase_name],collection_spent,0,work_deadline,time.time())
                if cap<=60: raise TimeoutError('no remaining cumulative collection budget')
                bound=e.phase_spec(phase_name,binding,endpoint,phase/'CAPTURE_SPEC.json',cap)
                command=[str(c.NATIVE_PYTHON),str(e.ROOT/'driver.py'),'collect','--spec',str(phase/'CAPTURE_SPEC.json'),'--output',str(phase/'rollout')]
                c.write_once(phase/'COLLECT_COMMAND.json',{'argv':command,'cap_seconds':cap,'collector_gpu_visible':False,
                    'collection_spent_before':collection_spent,'shared_work_deadline_epoch':work_deadline})
                collected_at=time.time()
                try: coordinator.owned_command(command,phase/'collection.log',min(cap+30,work_deadline-time.time()))
                finally: collection_spent+=time.time()-collected_at
                status=c.read(phase/'rollout/STATUS.json')
                statuses.append({'phase':phase_name,'weight':weight,**status})
                if status['recorded']!=len(bound['plan']) or status['stop_reason'] is not None:
                    raise RuntimeError('incomplete/capped phase retained without retry')
            finally: life.stop_service(service_dir/'service')
    except BaseException as caught:
        error={'type':type(caught).__name__,'message':str(caught)}
    terminal={'complete':error is None,'error':error,'statuses':statuses,'collection_elapsed_seconds':collection_spent,
        'elapsed_seconds':time.time()-started,'deadline_epoch':deadline,'work_deadline_epoch':work_deadline,
        'global_cap_overrun_seconds':max(0,time.time()-deadline),
        'owned_service_release_records':[str(p) for p in output.glob('services/*/SERVICE_STOPPED.json')],
        'cpu_analysis':'Explicit analyze after coordinator releases GPU authority; no in-lock analysis.'}
    c.write_once(output/'TERMINAL.json',terminal)
    return terminal


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('verify','collect','run','analyze'))
    parser.add_argument('--output',type=Path,default=e.ROOT/'outputs/attempt-001')
    parser.add_argument('--spec',type=Path)
    args=parser.parse_args()
    if args.command=='collect': raise SystemExit(asyncio.run(collect(args.spec,args.output)))
    if args.command=='run':
        with (e.ROOT/'COORDINATOR.lock').open('a') as lease:
            fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            value=run(args.output)
        print(json.dumps(value,sort_keys=True))
        raise SystemExit(0 if value['complete'] else 1)
    value=verify_ready() if args.command=='verify' else results.analyze(args.output)
    print(json.dumps({'command':args.command,'gpu_calls':0,'planned':len(value.get('plan',[])) or value.get('planned')}))
