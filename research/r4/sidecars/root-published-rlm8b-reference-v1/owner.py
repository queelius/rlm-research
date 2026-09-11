"""Serial full-weight phases; mandatory second-policy reserve, exact ownership."""
import argparse,os,re,signal,subprocess,time
from pathlib import Path
import rv_study as s,rv_protocol as p
class MainTermination(BaseException):pass
def release_containers(directory):
    safe=True
    for path in sorted((directory/'rollout/episodes').glob('*/worker/CONTAINER_COMMAND.json')):
        stopped=path.parent/'CONTAINER_STOPPED.json'
        if stopped.exists() and s.read(stopped).get('returncode')==0:continue
        name=s.read(path)['name']
        if not re.fullmatch(r'rv8b-[a-f0-9]{32}',name):raise ValueError('invalid recorded owned container name')
        try:
            result=subprocess.run([str(s.RUNTIME/'bin/docker'),'rm','--force','--ignore',name],capture_output=True,text=True,timeout=20)
            value=dict(name=name,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr);safe &= result.returncode==0
        except Exception as e:value=dict(name=name,error=f'{type(e).__name__}: {e}');safe=False
        s.write(path.parent/'OWNER_CONTAINER_RELEASE.json',value)
    return safe
def harvest(output,policy):
    root=output/policy/'rollout';aggregate=s.read(root/'ROWS.json') if (root/'ROWS.json').exists() else []
    indexed={r['coordinate']['id']:r for r in aggregate};values=[]
    for row in p.plan():
        if row['policy']!=policy:continue
        directory=root/'episodes'/row['id'];path=directory/'RESULT.json'
        value=s.read(path) if path.exists() else indexed.get(row['id'])
        if value is not None:
            if value['coordinate']!=row:raise ValueError('harvest coordinate mismatch')
        else:
            value=p.null(row,'no authenticated completed endpoint; partial calls retained')
            calls=[]
            for call in sorted((directory/'calls').glob('*')):
                if (call/'RESULT.json').exists():calls.append(s.read(call/'RESULT.json'))
                elif (call/'REQUEST.json').exists():
                    response=s.read(call/'RESPONSE.json') if (call/'RESPONSE.json').exists() else None
                    try:usage=__import__('json').loads(response['body']).get('usage') if response else None
                    except (ValueError,AttributeError):usage=None
                    calls.append(dict(physical_attempt=True,native_verified=False,usage=usage,interrupted=True,request_path=str(call/'REQUEST.json'),response_path=str(call/'RESPONSE.json') if response else None))
            value['calls']=calls
        values.append(value)
    return values
def binding(policy):return dict(schema='published8b-full-weight-package-v1',policy=policy,checkpoint=s.MODELS[policy],model_manifest_sha256=s.sha(Path(s.MODELS[policy]['path'])/'local-research-manifest.json'),template_sha256=s.sha(s.TEMPLATE),adapter=None)
def collector_argv(policy,deadline):
    root=s.ATTEMPT/policy;argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--policy',policy,'--endpoint',str(root/'service/endpoint-original.json'),'--output',str(root/'rollout'),'--deadline',str(deadline)];validate_argv(argv);return argv
def validate_argv(argv):
    if len(argv)!=10 or argv[:3]!=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--policy'] or argv[4]!='--endpoint' or argv[6]!='--output' or argv[8]!='--deadline' or argv[3] not in ('base','rlm'):raise ValueError('exact collector CLI')
    policy=argv[3];root=s.ATTEMPT/policy
    if Path(argv[5]).resolve()!=root/'service/endpoint-original.json' or Path(argv[7]).resolve()!=root/'rollout':raise ValueError('collector namespace')
    return dict(policy=policy,deadline=float(argv[9]))
def phase_deadline(start,now,work,policy):return min(start+1620,work-1710) if policy=='base' else min(now+1620,work-90)
def preflight(directory,value):
    import httpx
    endpoint=s.read(directory/'endpoint-original.json');model=s.MODELS[value['policy']];config=s.read(directory/'inference.json')['vllm']
    if endpoint['base_model']!=model or endpoint.get('adapter') is not None or config['model']!=model['path'] or config['max_model_len']!=32768 or config['enable_lora'] or config['chat_template']!=str(s.TEMPLATE):raise ValueError('actual 8B config/descriptor binding')
    with httpx.Client(headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]},trust_env=False,timeout=20) as client:
        base=f'http://{endpoint["host"]}:{endpoint["port"]}';version=client.get(base+'/version');version.raise_for_status();models=client.get(base+'/v1/models');models.raise_for_status()
    cards=models.json().get('data',[])
    if version.json().get('version')!='0.28.0' or len(cards)!=1 or cards[0].get('id')!=model['alias'] or cards[0].get('root')!=model['path'] or cards[0].get('parent') is not None:raise ValueError('served model/version identity')
    s.write(directory.parent/'PREFLIGHT.json',dict(version=version.json(),models=models.json(),binding_sha256=s.digest(value),epoch=time.time()))
def suite():
    value=s.load('rv8b_actual_suite',s.SIDE/'leaf-post-sft-suite-v1/suite.py','6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1');value.verify()
    with s.aliases({'study':s}):life=s.load('rv8b_actual_lifecycle',s.SIDE/'leaf-free-id-correspondence-v1/lifecycle_adapter_v3.py','759f527bbd35d866b681641262a7c21625390c233ba4e17f7c3b7ded2f443a8f')
    life.install(value);value.SERVE=s.ROOT/'service.py';value.life.ALLOCATION_SERVICE=value.SERVE;value.preflight=preflight;return value
def execute(output):
    ready=s.verify();private=s.load('rv8b_private_preflight',s.RUNTIME/'credential_preflight.py','2ff11844d7237f99d1d6080b2e599a1bacf34ad693e13acd98a41cddcaaa8110').require_provider_credential()
    if output.resolve()!=s.ATTEMPT or output.exists():raise ValueError('unused exact attempt required')
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must assign one GPU')
    runner=suite();start=time.time();work=start+3330;owned=start+3480;output.mkdir(parents=True)
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',[p.null(r,'before launch') for r in p.plan()]);s.write(output/'OWNER_RUN.json',dict(identity=ready['identity'],started_epoch=start,work_deadline=work,owned_deadline=owned,outer_seconds=3600,private_credential_check=private))
    cancelled=False
    def expired(signum,*_):
        nonlocal cancelled
        cancelled=True
        if signum in (signal.SIGINT,signal.SIGTERM):raise MainTermination('MAIN cancellation')
        raise TimeoutError('owned3480 deadline')
    previous={sig:signal.signal(sig,expired) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)};signal.setitimer(signal.ITIMER_REAL,max(.1,owned-time.time()));phases=[];unsafe=False
    try:
        for policy in ('base','rlm'):
            if cancelled:break
            directory=output/policy;directory.mkdir();end=phase_deadline(start,time.time(),work,policy);error=release_error=None;released=False
            try:
                if unsafe:raise RuntimeError('previous owned service not released')
                runner.start_service(directory,binding(policy),min(end-30,time.time()+150))
                until=end-30;runner.command(directory,'collect-'+policy,collector_argv(policy,until),max(.1,until-time.time()),until)
            except BaseException as e:error=dict(type=type(e).__name__,message=str(e))
            finally:
                try:runner.release_service(directory);released=True
                except BaseException as e:release_error=dict(type=type(e).__name__,message=str(e));unsafe=True
                try:
                    if not release_containers(directory):raise RuntimeError('owned container not released')
                except BaseException as e:release_error=dict(type=type(e).__name__,message=str(e));unsafe=True;released=False
            phase=dict(policy=policy,error=error,release_error=release_error,released=released,elapsed_seconds=time.time()-start);s.write(directory/'PHASE_TERMINAL.json',phase);phases.append(phase)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    rows=[row for policy in ('base','rlm') for row in harvest(output,policy)]
    s.write(output/'ROWS.json',rows);result=dict(complete=len(phases)==2 and all(p['released'] and p['error'] is None for p in phases),phases=phases,planned=48,recorded=len(rows),elapsed_seconds=time.time()-start,active_service=unsafe,cancelled=cancelled)
    s.write(output/'OWNER_TERMINAL.json',result);return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);a=ap.parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:r=execute(a.output);print(r);raise SystemExit(0 if r['complete'] else 1)
