"""MAIN-only two sequential released services, bounded science and exact owned release."""
import argparse
import ast
import json
import os
import signal
import time
import traceback
import study as s
import service


def error_record(error):
    text=traceback.format_exc();message=str(error)
    for key,value in os.environ.items():
        if len(value)>=6 and any(x in key.upper() for x in ('API_KEY','TOKEN','PASSWORD','SECRET')):
            text=text.replace(value,'[REDACTED]');message=message.replace(value,'[REDACTED]')
    return {'type':type(error).__name__,'message':message,'traceback':text,'locals_included':False}


def dependencies():
    suite=s.short().dependencies()
    source=s.SIDE/'root-rlvr-campaign-v1/campaign_lifecycle_v2.py'
    assert s.sha(source)=='568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5'
    text=source.read_text();node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='claim_service')
    claim=ast.get_source_segment(text,node);before='c.ROLE / "source/serve.py"'
    assert claim.count(before)==2
    suite.SERVE=s.ROOT/'service.py';suite.life.ALLOCATION_SERVICE=suite.SERVE
    exec(compile(claim.replace(before,'ALLOCATION_SERVICE'),str(source)+':controller-screen','exec'),suite.life.__dict__)
    suite.preflight=preflight
    return suite


def preflight(directory,binding):
    import httpx
    arm=binding['arm'];endpoint=s.read(directory/'endpoint-original.json')
    s.qwen_service().validate_descriptor(endpoint,s.MODELS[arm])
    actual=s.read(directory/'inference.json')
    assert actual==service.config(arm,directory,os.environ[endpoint['api_key_env']])
    with httpx.Client(headers={'Authorization':'Bearer '+os.environ[endpoint['api_key_env']]},trust_env=False,timeout=20) as client:
        url=f"http://{endpoint['host']}:{endpoint['port']}"
        version=client.get(url+'/version');version.raise_for_status();assert version.json()['version']=='0.28.0'
        models=client.get(url+'/v1/models');models.raise_for_status()
        s.qwen_service().validate_models(models.json(),s.MODELS[arm])
    s.write_x(directory.parent/'PREFLIGHT.json',{'version':version.json(),'models':models.json(),
        'inference_sha256':s.sha(directory/'inference.json'),'binding':binding})


def execute():
    ready=s.verify();assert not s.ATTEMPT.exists()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    assert gpu and ',' not in gpu and os.environ.get('STRICT_RLM_CALIBRATION_API_KEY')
    started=time.time();end=started+s.OWNER_SECONDS;s.ATTEMPT.mkdir(parents=True)
    s.write_x(s.ATTEMPT/'OWNER_RUN.json',{'ready_sha256':s.sha(s.ROOT/'READY.json'),'identity':ready['identity'],
        'started_epoch':started,'owner_cap_seconds':1800,'science_total_cap_seconds':1200,'arm_order':list(s.ARMS)})
    def stop(sig,frame):raise TimeoutError('owner signal '+str(sig))
    previous={sig:signal.signal(sig,stop) for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL,s.OWNER_SECONDS-75)
    stages=[];suite=dependencies()
    try:
        for arm in s.ARMS:
            if time.time()>=end-90:break
            directory=s.ATTEMPT/arm;directory.mkdir();errors=[];released=False;began=time.time()
            try:
                suite.start_service(directory,s.binding(arm),min(time.time()+285,end-90))
                science_started=time.time();deadline=min(science_started+600,end-90)
                argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--arm',arm,'--endpoint',
                    str(directory/'service/endpoint-original.json'),'--output',str(directory/'science'),
                    '--deadline',str(deadline)]
                suite.command(directory,'science',argv,max(.001,deadline-time.time()+15),end-75)
            except BaseException as error:errors.append({'stage':'science_or_start',**error_record(error)})
            finally:
                cleanup=time.time()
                try:
                    suite.release_service(directory)
                    receipt=s.read(directory/'SERVICE_STOPPED.json')
                    released=bool(receipt['all_owned_process_identities_exited'] and receipt['ports_free'])
                except BaseException as error:errors.append({'stage':'release',**error_record(error)})
                value={'arm':arm,'elapsed_seconds':time.time()-began,'released':released,'errors':errors,
                       'cleanup_seconds':time.time()-cleanup}
                s.write_x(directory/'STAGE_TERMINAL.json',value);stages.append(value)
            if not released:break
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    result={'stages':stages,'elapsed_seconds':time.time()-started,'planned_arms':2,
        'complete':len(stages)==2 and all(not x['errors'] and x['released'] for x in stages),
        'released':all(x['released'] for x in stages),'optimizer_steps':0}
    s.write_x(s.ATTEMPT/'OWNER_TERMINAL.json',result)
    import compare
    s.write_x(s.ATTEMPT/'PAIRED.json',compare.report())
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);a=p.parse_args()
    if a.command=='verify':s.verify();dependencies();print('source, models, native lifecycle verified; no GPU')
    else:
        result=execute();print(json.dumps(result));raise SystemExit(0 if result['complete'] else 1)
