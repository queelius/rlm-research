"""Parent-invoked one-service envelope; inherited MIG/environment and owned cleanup."""
import argparse
import ast
import fcntl
import json
import os
import signal
import sys
import time
from pathlib import Path
import experiment as e
import runtime as r

SUITE=r.SIDE/'leaf-post-sft-suite-v1/suite.py'
SUITE_SHA='6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1'
OBSERVER=r.SIDE/'root-seed-lifecycle-continuation-v1/driver.py'
OBSERVER_SHA='bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd'


def load_suite():
    suite=r.checked_import('suffix_owned_frozen_suite',SUITE,SUITE_SHA)
    if r.file_hash(OBSERVER)!=OBSERVER_SHA: raise ValueError('qualified process-absence fix changed')
    node=next(n for n in ast.parse(OBSERVER.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='observe_or_absent')
    scope={}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(OBSERVER),'exec'),scope)
    original=suite.life.v1.process_identity
    suite.life.v1.process_identity=lambda pid:scope['observe_or_absent'](original,pid)
    return suite


def verify_ready():
    value=e.verify()
    ready=r.read(r.ROOT/'READY.json')
    for path,sha in ready['artifact_sha256'].items():
        if r.file_hash(path)!=sha: raise ValueError('READY artifact changed: '+path)
    if ready['spec_sha256']!=r.file_hash(r.ROOT/'SPEC.json') or ready['planned']!=16:
        raise ValueError('READY study mismatch')
    return value


def execute(output,suite,spec,started):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    deadline,work_deadline=started+1800,started+1680
    r.write_once(output/'RUN.json',{'started_epoch':started,'deadline_epoch':deadline,
        'work_deadline_epoch':work_deadline,'collection_cap_seconds':1500,'dispatch_ceiling':2048,
        'gpu':os.environ.get('CUDA_VISIBLE_DEVICES'),'ownership':'unchanged V2 plus qualified process-absence observer'})
    error=None
    try:
        suite.start_service(output,spec['role_binding'],started+180)
        cap=min(1500,work_deadline-time.time()-30)
        if cap<=60: raise TimeoutError('no collection budget after setup')
        bound=output/'CAPTURE_SPEC.json'
        e.bind(output/'service/endpoint-original.json',output/'BINDING.json',bound,cap)
        suite.command(output,'collect',[suite.PYTHON,str(r.ROOT/'driver.py'),'collect',
            '--spec',str(bound),'--output',str(output/'rollout')],cap+30,work_deadline)
        status=r.read(output/'rollout/STATUS.json')
        dispatch=r.read(output/'rollout-routing/DISPATCH_STATUS.json')
        if status['recorded']!=16 or status['stop_reason'] is not None or dispatch['cap_exhausted']:
            raise RuntimeError('incomplete/capped study retained without retry')
    except BaseException as caught:
        error={'type':type(caught).__name__,'message':str(caught)}
    finally:
        try: suite.release_service(output)
        except BaseException as caught:
            error={'prior_error':error,'type':type(caught).__name__,'message':str(caught),'stage':'owned cleanup'}
    result={'complete':error is None,'error':error,'elapsed_seconds':time.time()-started,
        'deadline_epoch':deadline,'global_cap_overrun_seconds':max(0,time.time()-deadline),
        'release_marker':str(output/'SERVICE_STOPPED.json'),
        'release_record_exists':(output/'SERVICE_STOPPED.json').exists(),
        'partial_outcomes_preserved':True,'analysis_command':[sys.executable,
            str(r.ROOT/'driver.py'),'analyze','--output',str(output)]}
    r.write_once(output/'TERMINAL.json',result)
    return result


def main():
    started=time.time()
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--output',type=Path,default=r.ROOT/'outputs/attempt-001')
    args=parser.parse_args()
    spec=verify_ready()
    suite=load_suite()
    if args.verify:
        print(json.dumps({'verified':True,'planned':16,'gpu_calls':0}));return
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES'] or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('parent must assign exclusive GPU and existing credential')
    def interrupted(sig,frame): raise KeyboardInterrupt(f'owned suffix signal{sig}; release authenticated service')
    signal.signal(signal.SIGINT,interrupted)
    signal.signal(signal.SIGTERM,interrupted)
    with (r.ROOT/'COORDINATOR.lock').open('a') as lease:
        fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        result=execute(args.output.resolve(),suite,spec,started)
    print(json.dumps(result))
    raise SystemExit(0 if result['complete'] else 1)


if __name__=='__main__': main()
