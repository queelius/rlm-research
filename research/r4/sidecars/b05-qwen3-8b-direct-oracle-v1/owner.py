"""Exclusive owner for eight cached-Qwen3-8B B05 calibration calls."""
import json,os,signal,time,traceback
from pathlib import Path
import httpx
import collect,study

def preflight(service,binding):
    endpoint=study.read(service/'endpoint-original.json');assert endpoint['model_alias']==study.MODEL_ALIAS and Path(endpoint['base_model']['path']).resolve()==study.MODEL.resolve()
    key=os.environ[endpoint['api_key_env']];url=f"http://{endpoint['host']}:{endpoint['port']}"
    with httpx.Client(headers={'Authorization':'Bearer '+key},trust_env=False,timeout=30) as client:
        version=client.get(url+'/version');models=client.get(url+'/v1/models');version.raise_for_status();models.raise_for_status()
    cards={x['id']:x for x in models.json()['data']};assert cards[study.MODEL_ALIAS]['root']==str(study.MODEL)
    study.write_x(service.parent/'PREFLIGHT.json',{'version':version.json(),'models':models.json(),'binding_sha256':study.digest(binding)})

def summarize(runtime_ok):
    records=[study.read(p) for p in sorted((study.ATTEMPT/'calls').glob('*.json'))];plan={study.call_id(x):x for x in study.calls()};errors=[]
    if set(plan)!={r['call_id'] for r in records}:errors.append('call inventory differs')
    by_kind={}
    for kind in ('direct','oracle_exact_report_synthesis'):
        rows=[r for r in records if r['kind']==kind];by_kind[kind]={'planned':4,'accounted':len(rows),'transport_valid':sum(r['transport_valid'] for r in rows),'source_correct':sum((r.get('source_grade') or {}).get('status')=='correct' for r in rows),'source_valid_wrong':sum((r.get('source_grade') or {}).get('status')=='valid_but_wrong' for r in rows),'source_invalid':sum((r.get('source_grade') or {}).get('status') not in ('correct','valid_but_wrong') for r in rows),'prompt_tokens':sum((r.get('usage') or {}).get('prompt_tokens',0) for r in rows if r.get('transport_valid')),'completion_tokens':sum((r.get('usage') or {}).get('completion_tokens',0) for r in rows if r.get('transport_valid'))}
    complete=not errors and runtime_ok and len(records)==8 and all(r.get('transport_valid') for r in records)
    return {'schema':'b05-qwen3-8b-direct-oracle-result-v1','complete':complete,'planned':8,'accounted':len(records),'runtime_qualified':runtime_ok,'by_kind':by_kind,'errors':errors,'optimizer_steps':0,'model_alternative_not_pure_capacity_effect':True}

def execute(seconds=study.OWNER_SECONDS):
    ready=study.verify();assert seconds==study.OWNER_SECONDS and not study.ATTEMPT.exists();gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):raise ValueError('MAIN-owned GPU/private credential required')
    start=time.time();end=start+seconds;study.ATTEMPT.mkdir(parents=True);service=study.ATTEMPT/'service';service.mkdir();binding=study.binding();study.write_x(study.ATTEMPT/'BINDING.json',binding);study.write_x(study.ATTEMPT/'OWNER_RUN.json',{'ready_identity':ready['identity'],'planned':8,'owner_seconds':seconds,'science_seconds':study.SCIENCE_SECONDS,'started_epoch':start,'optimizer_steps':0})
    source=study.source();base=source.base_owner();suite=None;released=False;errors=[];runtime_ok=False
    def stop(*_):raise TimeoutError('bounded owner interrupted')
    previous={s:signal.signal(s,stop) for s in (signal.SIGALRM,signal.SIGTERM,signal.SIGINT)};signal.setitimer(signal.ITIMER_REAL,seconds-20)
    try:
        suite=base.study.dependencies();suite.SERVE=study.SERVICE;suite.life.__dict__['ALLOCATION_SERVICE']=study.SERVICE;suite.preflight=preflight
        suite.start_service(service,binding,min(start+285,end-50));descriptor=study.read(service/'service/endpoint-original.json');endpoint=f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        science=time.time();value=collect.execute(endpoint,study.ATTEMPT,min(science+study.SCIENCE_SECONDS,end-50));study.write_x(study.ATTEMPT/'COLLECTION.json',value);errors.extend(value['errors'])
    except BaseException as e:errors.append({'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(1,end-time.time()))
        if suite:
            try:suite.release_service(service);released=True
            except BaseException as e:errors.append({'stage':'release','type':type(e).__name__,'message':str(e)})
        else:released=True
        dispatch=service/'service/ACTUAL_DISPATCH.json'
        if dispatch.exists() and released:
            d=study.read(dispatch);runtime_ok=bool(d.get('environment_flag')=='1' and d.get('installed_batch_invariant_mode') is True and d.get('device_type')=='cuda' and d.get('original_function_returned') is True and d.get('instrumentation_sha256')==study.sha(study.MUSIQUE/'report_worker.py'))
        result=summarize(runtime_ok);result['errors'].extend(errors);result['complete']=bool(result['complete'] and not errors and released);result['released']=released;study.write_x(study.ATTEMPT/'RESULT.json',result)
        terminal={'complete':result['complete'],'released':released,'runtime_qualified':runtime_ok,'elapsed_seconds':time.time()-start,'errors':errors,'result_sha256':study.sha(study.ATTEMPT/'RESULT.json')};study.write_x(study.ATTEMPT/'OWNER_TERMINAL.json',terminal)
        signal.setitimer(signal.ITIMER_REAL,0)
        for s,h in previous.items():signal.signal(s,h)
    return terminal
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(study.verify()['identity'])
    else:
        r=execute(a.outer_seconds);print(json.dumps(r));raise SystemExit(0 if r['complete'] else 1)
