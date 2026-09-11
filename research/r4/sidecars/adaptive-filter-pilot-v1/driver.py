"""One fixed-policy service, inherited collector, one inclusive allocation clock."""
import argparse
import asyncio
import contextlib
import copy
import fcntl
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
import experiment as e
import results

saved=sys.modules['experiment'];sys.modules['experiment']=e.prior
try:
    upstream=e.checked_import('adaptive_pinned_owned_driver',e.ROOT.parent/'root-receipt-uptake-v1/driver.py',
        '1c18439c6bff52a734c8ed178fa6188171fef33b342b9d5aa29d71459d1530e8')
finally:sys.modules['experiment']=saved
sys.path.insert(0,str(e.ROOT))
c=e.c
life,coordinator=upstream.inherited.lifecycle,upstream.inherited.coordinator


def collection_deadline(started,now):
    return min(started+2580-120,now+2280)


def verify():
    spec=c.read(e.ROOT/'SPEC.json')
    c.authenticate(spec['source_file_sha256'])
    from prepare import plan_for
    plan,logical=plan_for(c.read(e.ROOT/'inputs/PUBLIC.json'))
    if plan!=spec['plan'] or logical!=spec['logical_cells'] or spec['binding']!=e.binding_for(spec['policy']):
        raise ValueError('frozen adaptive coordinates or binding changed')
    if spec['environment']!=e.environment_config():raise ValueError('timeouts/environment changed')
    tasks=e.make_tasks()
    for task in spec['tasks']:
        if tasks[task['name']].hash!=task['task_hash']:raise ValueError('physical task changed')
    return spec


def verify_ready():
    spec=verify();ready=c.read(e.ROOT/'READY.json')
    c.authenticate(ready['artifact_sha256'])
    if ready['spec_sha256']!=c.file_hash(e.ROOT/'SPEC.json') or ready['driver_sha256']!=c.file_hash(Path(__file__)):
        raise ValueError('READY binding changed')
    return spec


@contextlib.contextmanager
def collector_adapters():
    q=e.capture.q;base=e.collector()
    saved=q.make_context,q.request_metadata
    q.make_context,q.request_metadata=e.make_context,e.capture.native.request_metadata
    base.with_prompt,base.crossover_metrics=e.with_prompt,results.episode_metrics
    base.summarize,base.STUDY=results.summarize,e.ROOT.name
    try:yield base
    finally:q.make_context,q.request_metadata=saved


async def collect(spec_path,output):
    parent=verify();spec=c.read(spec_path)
    c.authenticate(spec['source_file_sha256'])
    for key in ('plan','logical_cells','tasks','binding','policy','environment'):
        if spec[key]!=parent[key]:raise ValueError('phase changes '+key)
    if spec['parent_spec_sha256']!=c.file_hash(e.ROOT/'SPEC.json'):raise ValueError('phase parent changed')
    if not 0<spec['wall_time_cap_seconds']<=2280:raise ValueError('collection cap changed')
    run=c.read(Path(spec_path).parent/'RUN.json')
    if spec['collection_deadline_epoch']>run['work_deadline_epoch']-120:raise ValueError('absolute deadline expanded')
    endpoint=spec['endpoint'];descriptor=c.read(spec['endpoint_descriptor_path'])
    expected=e.old.planned_endpoint(spec['binding'])
    model=spec['binding']['models'][spec['binding']['role_map']['root']]
    if (descriptor['adapter']!={'path':model['path'],'model_sha256':model['adapter_sha256'],'config_sha256':model['config_sha256']}
        or descriptor['model_alias']!=expected['model'] or descriptor['role_binding_sha256']!=c.file_hash(spec['binding_path'])
        or c.read(spec['binding_path'])!=spec['binding']
        or descriptor['base_model']['path']!=c.pilot_recipe()['base_model']
        or descriptor['base_model']['manifest_sha256']!=c.pilot_recipe()['base_manifest_sha256']):raise ValueError('physical service binding differs')
    if endpoint!={**expected,'url':f"http://{descriptor['host']}:{descriptor['port']}/v1",'api_key_env':descriptor['api_key_env']}:
        raise ValueError('physical endpoint changed')
    e.capture.recursive.validate_serving_evidence(spec['serving_evidence'])
    request=urllib.request.Request(endpoint['url']+'/models',headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]})
    with urllib.request.urlopen(request,timeout=15) as response:cards={r['id']:r for r in json.load(response)['data']}
    for alias,model in spec['binding']['models'].items():
        if Path(cards[alias].get('root','')).resolve()!=Path(model['path']).resolve() or cards[alias].get('parent')!=endpoint['renderer_model']:
            raise ValueError('advertised alias/base/adapter mismatch')
    output=Path(output);audit=output.with_name(output.name+'-routing')
    if output.exists() or audit.exists():raise ValueError('unused attempt only; no retry')
    os.environ['PATH']=str(e.capture.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    c.write_once(audit/'BINDING.json',{'binding':spec['binding'],'advertised':cards})
    with collector_adapters() as base,e.installed_hooks(spec['binding'],audit):
        return await base.run(argparse.Namespace(endpoint_url=None,output_dir=output,resume=False),copy.deepcopy(spec),e.make_tasks())


def run(output):
    started=time.time();work_deadline=started+2580;deadline=started+2700
    spec=verify_ready()
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES'] or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('main assigns exclusive GPU and existing credential')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    c.write_once(output/'RUN.json',{'started_epoch':started,'work_deadline_epoch':work_deadline,'deadline_epoch':deadline,
        'ready_sha256':c.file_hash(e.ROOT/'READY.json'),'spec_sha256':c.file_hash(e.ROOT/'SPEC.json'),
        'physical_planned':40,'logical_cells':48,'collection_cap_seconds':2280})
    upstream.install_observer(coordinator);life.install();e.native.binding_for=e.binding_for
    error=None;status=None;service=output/'service'
    try:
        binding,endpoint=coordinator.start_service(service,spec['policy'],min(work_deadline,started+180))
        try:
            now=time.time();collection_end=collection_deadline(started,now)
            if collection_end-now<=60:raise TimeoutError('no cumulative collection budget')
            descriptor=c.read(endpoint)
            phase=copy.deepcopy(spec)
            phase.update(endpoint={**e.old.planned_endpoint(spec['binding']),'url':f"http://{descriptor['host']}:{descriptor['port']}/v1",'api_key_env':descriptor['api_key_env']},
                binding_path=str(binding),endpoint_descriptor_path=str(endpoint),parent_spec_sha256=c.file_hash(e.ROOT/'SPEC.json'),
                serving_evidence=e.capture.recursive.serving_evidence(Path(endpoint).parent/'inference.log'),
                collection_deadline_epoch=collection_end,wall_time_cap_seconds=collection_end-now)
            phase['source_file_sha256'].update({str(p):c.file_hash(p) for p in (Path(binding),Path(endpoint),e.ROOT/'SPEC.json',e.ROOT/'READY.json')})
            c.write_once(output/'CAPTURE_SPEC.json',phase)
            argv=[str(c.NATIVE_PYTHON),str(e.ROOT/'driver.py'),'collect','--spec',str(output/'CAPTURE_SPEC.json'),'--output',str(output/'rollout')]
            c.write_once(output/'COLLECT_COMMAND.json',{'argv':argv,'collection_deadline_epoch':collection_end,'work_deadline_epoch':work_deadline})
            coordinator.owned_command(argv,output/'collection.log',min(collection_end-time.time()+30,work_deadline-time.time()))
            status=c.read(output/'rollout/STATUS.json')
            if status['recorded']!=40 or status['stop_reason'] is not None:raise RuntimeError('incomplete/capped collection retained, no retry')
        finally:life.stop_service(service/'service')
    except BaseException as caught:error={'type':type(caught).__name__,'message':str(caught)}
    terminal={'complete':error is None,'error':error,'status':status,'elapsed_seconds':time.time()-started,
        'deadline_epoch':deadline,'work_deadline_epoch':work_deadline,'cap_overrun_seconds':max(0,time.time()-deadline),
        'analysis':'Explicit CPU analyze after owned service release; no outcome selection.'}
    c.write_once(output/'TERMINAL.json',terminal)
    return terminal


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run','collect','analyze'))
    parser.add_argument('--output',type=Path,default=e.ROOT/'outputs/attempt-001');parser.add_argument('--spec',type=Path)
    args=parser.parse_args()
    if args.command=='collect':raise SystemExit(asyncio.run(collect(args.spec,args.output)))
    if args.command=='run':
        with (e.ROOT/'COORDINATOR.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);result=run(args.output.resolve())
        print(json.dumps(result));raise SystemExit(0 if result['complete'] else 1)
    value=verify_ready() if args.command=='verify' else results.analyze(args.output)
    print(json.dumps({'command':args.command,'planned':len(value.get('plan',[])) or value.get('planned'),'gpu_calls':0}))
