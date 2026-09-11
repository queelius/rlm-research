"""Parent-only bounded service; CPU preparation never calls run."""
import argparse
import asyncio
import copy
import fcntl
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
import experiment as e
import hooks
import results

saved=sys.modules.get('study');sys.modules['study']=e.old;sys.path.insert(0,str(e.old.ROOT))
inherited=e.checked_import('typed_owned_driver',e.old.ROOT/'driver.py','c2ff3561af4cee9f46a989f19dc2f9d6d3cc9f2c6ba3410fd1a5fc07b4e7d4b2')
if saved is None: sys.modules.pop('study',None)
else: sys.modules['study']=saved
sys.path.insert(0,str(e.ROOT));c=e.c

async def collect(spec_path,output):
    spec=e.verify_phase(spec_path);output=Path(output);audit=output.with_name(output.name+'-routing')
    if output.exists() or audit.exists(): raise ValueError('unused capture required; no retry')
    endpoint=spec['endpoint'];req=urllib.request.Request(endpoint['url']+'/models',headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]})
    with urllib.request.urlopen(req,timeout=15) as response: cards={r['id']:r for r in json.load(response)['data']}
    for alias,model in spec['role_binding']['models'].items():
        card=cards.get(alias,{})
        if Path(card.get('root','')).resolve()!=Path(model['path']).resolve() or card.get('parent')!=endpoint['renderer_model']: raise ValueError('live binding mismatch')
    hooks.configure_runtime();collector=e.collector();q=collector.q
    saved=q.make_context,q.request_metadata
    q.make_context,q.request_metadata=e.make_context,e.capture.native.request_metadata
    collector.with_prompt=e.with_prompt;collector.crossover_metrics=results.episode_metrics;collector.summarize=results.summarize;collector.STUDY=e.ROOT.name
    c.write_once(audit/'BINDING.json',{'binding':spec['role_binding'],'advertised':cards})
    try:
        with hooks.installed(spec['role_binding'],audit,spec['plan'],c.read(e.ROOT/'inputs/PUBLIC_CATALOGS.json')):
            return await collector.run(argparse.Namespace(endpoint_url=None,output_dir=output,resume=False),copy.deepcopy(spec),e.make_tasks())
    finally: q.make_context,q.request_metadata=saved

def verify_ready():
    spec=e.verify();ready=c.read(e.ROOT/'READY.json');c.authenticate(ready['artifact_sha256'])
    if ready['planned']!=36 or ready['spec_sha256']!=c.file_hash(e.ROOT/'SPEC.json') or ready['driver_sha256']!=c.file_hash(Path(__file__)): raise ValueError('READY drift')
    return spec

def run(output):
    started=time.time();deadline=started+2400;work=started+2280;spec=verify_ready()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'): raise ValueError('main assigns GPU/credential')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    c.write_once(output/'RUN.json',{'started_epoch':started,'deadline_epoch':deadline,'work_deadline_epoch':work,
        'spec_sha256':c.file_hash(e.ROOT/'SPEC.json'),'ready_sha256':c.file_hash(e.ROOT/'READY.json'),'gpu':gpu})
    life,coordinator=inherited.lifecycle,inherited.coordinator
    observer=e.checked_import('typed_absence_observer',e.ROOT.parents[1]/'operations/2026-09-09-after-identity-receipt/receipt_driver.py','e2789bf5c4df114f8005f83dcfb68a909888995e2677c395a5d6de969b7a1c83')
    observer.install_observer(coordinator);life.install();e.native.binding_for=e.binding_for
    error=None;status=None;service=output/'services/step8';collection_elapsed=0
    try:
        binding,endpoint=coordinator.start_service(service,spec['policies']['step8'],work)
        try:
            phase=output/'phase-step8';phase.mkdir();cap=min(1800,work-time.time()-30)
            if cap<=60: raise TimeoutError('remaining shared collection envelope insufficient')
            e.phase_spec(binding,endpoint,phase/'CAPTURE_SPEC.json',cap)
            argv=[str(c.NATIVE_PYTHON),str(e.ROOT/'driver.py'),'collect','--spec',str(phase/'CAPTURE_SPEC.json'),'--output',str(phase/'rollout')]
            c.write_once(phase/'COLLECT_COMMAND.json',{'argv':argv,'cap_seconds':cap,'work_deadline_epoch':work})
            begin=time.time()
            try: coordinator.owned_command(argv,phase/'collection.log',min(cap,work-time.time()))
            finally: collection_elapsed=time.time()-begin
            status=c.read(phase/'rollout/STATUS.json')
            if status['recorded']!=36 or status['stop_reason'] is not None: raise RuntimeError('incomplete capture retained without retry')
        finally: life.stop_service(service/'service')
    except BaseException as caught: error={'type':type(caught).__name__,'message':str(caught)}
    terminal={'complete':error is None,'error':error,'status':status,'collection_elapsed_seconds':collection_elapsed,
        'elapsed_seconds':time.time()-started,'deadline_epoch':deadline,'global_cap_overrun_seconds':max(0,time.time()-deadline),
        'owned_service_release_records':[str(p) for p in output.glob('services/*/SERVICE_STOPPED.json')],
        'cpu_analysis':'Explicit post-terminal CPU projection, not inside GPU envelope.'}
    c.write_once(output/'TERMINAL.json',terminal);return terminal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','collect','run','analyze']);p.add_argument('--spec',type=Path);p.add_argument('--output',type=Path,default=e.ROOT/'outputs/attempt-001');args=p.parse_args()
    if args.command=='collect': raise SystemExit(asyncio.run(collect(args.spec,args.output)))
    if args.command=='run':
        with (e.ROOT/'COORDINATOR.lock').open('a') as lease:
            fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB);value=run(args.output)
        print(json.dumps(value));raise SystemExit(0 if value['complete'] else 1)
    value=verify_ready() if args.command=='verify' else results.analyze(args.output)
    print(json.dumps({'command':args.command,'planned':len(value.get('plan',[])) or value.get('planned'),'gpu_calls':0}))
