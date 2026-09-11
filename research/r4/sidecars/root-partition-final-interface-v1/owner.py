"""MAIN-only900s single released-base service, exact new owner→collector namespace."""
import argparse
import os
from pathlib import Path
import signal
import time
import study as s

def collector_argv(stage,output,deadline):
    argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(stage/'service/endpoint-original.json'),'--output',str(output/'rollout'),'--deadline',str(deadline)]
    validate_argv(argv);return argv

def validate_argv(argv):
    if len(argv)!=9 or argv[:4]!=[str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint'] or argv[5]!='--output' or argv[7]!='--deadline':raise ValueError('exact collector argv shape')
    endpoint=Path(argv[4]);output=Path(argv[6])
    if output.resolve()!=s.ATTEMPT/'rollout' or endpoint.resolve()!=s.ATTEMPT/'owned-service/service/endpoint-original.json':raise ValueError('exact new owner/collector namespace only')
    return dict(endpoint=endpoint,output=output,deadline=float(argv[8]))

def credential():
    module=s.load('partition_credential_preflight',s.RUNTIME/'credential_preflight.py','2ff11844d7237f99d1d6080b2e599a1bacf34ad693e13acd98a41cddcaaa8110')
    return module.require_provider_credential()

def binding():
    # Existing qualified wrapper verifies its exact original base WEIGHTS closure.
    return dict(schema='released-base-single-model-binding-v1',model='qwen3',checkpoint=s.MODEL,
        weights_sha256=s.sha(s.FREE/'WEIGHTS.json'),adapter=None)

def preflight(directory,value):
    import httpx
    endpoint=s.read(directory/'endpoint-original.json');s.service.validate_descriptor(endpoint,s.MODEL)
    config=s.read(directory/'inference.json')['vllm']
    if config.get('enable_lora') is not False or config.get('enable_prefix_caching') is not False:raise ValueError('base/no-cache service changed')
    headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]};url=f'http://{endpoint["host"]}:{endpoint["port"]}'
    with httpx.Client(headers=headers,trust_env=False,timeout=30) as client:
        version=client.get(url+'/version');version.raise_for_status();models=client.get(url+'/v1/models');models.raise_for_status()
    if version.json().get('version')!='0.28.0':raise ValueError('unqualified vLLM version')
    s.service.validate_models(models.json(),s.MODEL)
    s.write(directory.parent/'PREFLIGHT.json',dict(version=version.json(),models=models.json(),binding_sha256=s.digest(value),inference_sha256=s.sha(directory/'inference.json'),checked_epoch=time.time()))

def suite():
    value=s.load('partition_qualified_owned_suite',s.SIDE/'leaf-post-sft-suite-v1/suite.py','6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1')
    value.verify();s.lifecycle.install(value);value.preflight=preflight;return value

def execute(output):
    private=credential();ready=s.verify()
    if output.resolve()!=s.ATTEMPT or output.exists():raise ValueError('exact fresh attempt only')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must assign one owned GPU')
    runner=suite();started=time.time();work=started+780;owned=started+870
    output.mkdir(parents=True,exist_ok=False);stage=output/'owned-service';stage.mkdir()
    s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json'),started_epoch=started,work_deadline=work,owned_deadline=owned,outer_seconds=900,gpu=gpu,**private))
    def expired(*_):raise TimeoutError('owned870s inclusive deadline or MAIN termination')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,max(.001,owned-time.time()))
    error=release_error=terminal=None;released=False
    try:
        runner.start_service(stage,binding(),min(work,time.time()+180))
        deadline=min(work,time.time()+600);argv=collector_argv(stage,output,deadline)
        runner.command(stage,'partition-final-collect',argv,max(.001,deadline-time.time()),deadline)
        terminal=s.read(output/'rollout/STATUS.json')
        if terminal['planned']!=24 or terminal['recorded']!=24:raise ValueError('collector must retain24 planned slots')
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
    finally:
        try:runner.release_service(stage);released=True
        except BaseException as caught:release_error=dict(type=type(caught).__name__,message=str(caught))
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    result=dict(complete=error is None and released,error=error,release_error=release_error,released=released,collector_status=terminal,planned=24,elapsed_seconds=time.time()-started,main_owns_gpu_and_lock=True,no_retry=True)
    s.write(output/'OWNER_TERMINAL.json',result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);args=ap.parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(result);raise SystemExit(0 if result['complete'] else 1)
