"""Finite unattended breadth campaign. No Codex, remote model, or optimizer calls."""
from __future__ import annotations
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import runner

STORE=ROOT.parents[1]
ENV=Path('/project/alex_phd/envs/prime-rl-5990b1b')
LEGACY=STORE/'sidecars/strict-rlm-temperature-adherence-v1'
GPU='MIG-c0ac02b2-b43f-58cf-ab06-dc24b64b023a'
MODELS={
    '4b':'/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554',
    '8b':'/project/alex_phd/research-cache/models/Qwen--Qwen3-8B--b968826d9c46dd6066d109eabc6255188de91218',
}
STOP=threading.Event()

def extend(rows):
    available=[r for r in rows if r.get('available')]
    return len(available)>=8 and any(r.get('correct') for r in available) and any(not r.get('correct') for r in available)

def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()

def snapshot(path,value):
    temporary=path.with_name(path.name+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    temporary.replace(path)

def service(model,folder,deadline):
    spec=importlib.util.spec_from_file_location('breadth_existing_environment',LEGACY/'scripts/launch.py')
    helper=importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    for port in (18731,18741,18751):
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',port))==0: raise RuntimeError('service port already owned')
    folder.mkdir(parents=True,exist_ok=False)
    value=json.loads((LEGACY/'configs/inference-replica0.json').read_text())
    value['server']['port']=18731; value['backend_port']=18751
    value['vllm'].update(model=model,max_model_len=32768,data_parallel_rpc_port=18741,
        enable_lora=False,max_num_seqs=8,gpu_memory_utilization=.82,
        enforce_eager=True,api_key=[os.environ['BREADTH_LOCAL_API_KEY']])
    value['output_dir']=str(folder/'launcher')
    from prime_rl.configs.inference import InferenceConfig
    InferenceConfig.model_validate(value)
    runner.save(folder/'inference-private.json',value)
    (folder/'inference-private.json').chmod(0o600)
    env=helper._environment()
    env.update(CUDA_VISIBLE_DEVICES=GPU,HF_HUB_OFFLINE='1',HF_HOME='/project/alex_phd/research-cache/huggingface-runtime',
        LD_LIBRARY_PATH='/export/software/system/nvidia/580.126.20/lib:'+env.get('LD_LIBRARY_PATH',''),
        OMP_NUM_THREADS='4',WANDB_MODE='disabled',PYTHONDONTWRITEBYTECODE='1')
    # Reuse existing compiled kernels, but own the service and ports independently.
    command=[str(ENV/'bin/inference'),'@',str(folder/'inference-private.json')]
    log=(folder/'server.log').open('x')
    process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    import psutil
    runner.save(folder/'OWNER.json',{'pid':process.pid,'create_time':psutil.Process(process.pid).create_time(),
        'command':command,'gpu':GPU,'model':model,'started':time.time()})
    end=min(deadline,time.time()+300)
    from urllib.request import Request,urlopen
    while time.time()<end and not STOP.is_set():
        if process.poll() is not None: break
        try:
            request=Request('http://127.0.0.1:18731/v1/models',headers={'Authorization':'Bearer '+os.environ['BREADTH_LOCAL_API_KEY']})
            with urlopen(request,timeout=2) as response: body=json.load(response)
            if model in [row['id'] for row in body['data']]: return process,log,helper
        except Exception: pass
        time.sleep(2)
    helper._stop(process); log.close()
    raise RuntimeError('owned service did not become ready')

def summary(rows):
    groups=defaultdict(lambda:{'episodes':0,'available':0,'valid':0,'correct':0,'excluded':0,'input_tokens':0,'output_tokens':0,'calls':0})
    for row in rows:
        key='|'.join([row['model'],row['dataset'],row['arm'],str(row['chunks'])])
        item=groups[key]; item['episodes']+=1
        for field in ('available','valid','correct'): item[field]+=bool(row.get(field))
        item['excluded']+=bool(row.get('excluded'))
        cost=row.get('cost',{}); item['input_tokens']+=cost.get('prompt_tokens',0)
        item['output_tokens']+=cost.get('completion_tokens',0); item['calls']+=cost.get('physical_calls',0)
    return dict(groups)

def execute(args):
    from transformers import AutoTokenizer
    output=args.output.resolve(); output.mkdir(parents=True,exist_ok=True)
    lock=(STORE/'sidecars/root-rlvr-campaign-v1/COORDINATOR.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for sig in (signal.SIGTERM,signal.SIGINT): signal.signal(sig,lambda *_:STOP.set())
    lease=int(os.environ.get('SLURM_JOB_END_TIME','1789493416'))
    deadline=min(time.time()+args.hours*3600,lease-600)
    if deadline<=time.time()+180: raise RuntimeError('insufficient allocation remainder')
    plan={'cases_sha256':sha(args.cases),'source_sha256':{p.name:sha(p) for p in (ROOT/'runner.py',ROOT/'campaign.py')},
        'models':MODELS,'seed':202609140000,'temperature':.5,'max_context':32768,'shared_input_cap':24000,
        'phases':[[0,16,2],[16,80,2],[80,256,2],[256,512,2],[0,80,4]],
        'model_training':False,'dataset_role':'exploratory','deadline':deadline,
        'lease_end_from_environment':lease,'pilot_only':args.pilot_only,'limit_per_dataset':args.limit_per_dataset}
    if (output/'PLAN.json').exists():
        old=json.loads((output/'PLAN.json').read_text())
        assert old['cases_sha256']==plan['cases_sha256'] and old['source_sha256']==plan['source_sha256']
        assert old['pilot_only']==args.pilot_only and old['limit_per_dataset']==args.limit_per_dataset
    else: runner.save(output/'PLAN.json',plan)
    # Preserve initial plan; each resume has an explicit new lease receipt.
    invocation=uuid.uuid4().hex[:12]
    runner.save(output/f'ADMISSION-{invocation}.json',{'pid':os.getpid(),'started':time.time(),
        'deadline':deadline,'plan_sha256':sha(output/'PLAN.json'),'gpu':GPU})
    cases=[json.loads(line) for line in args.cases.read_text().splitlines()]
    grouped=defaultdict(list)
    for case in cases:
        case['answer']=case['metadata']['gold']
        grouped[case['dataset']].append(case)
    rows=[json.loads(p.read_text()) for p in output.glob('models/*/episodes/*.json')]
    failures=[]; skipped=[]; os.environ['BREADTH_LOCAL_API_KEY']=uuid.uuid4().hex
    phases=plan['phases'][:1] if args.pilot_only else plan['phases']
    try:
        for phase,(start,end,chunks) in enumerate(phases):
            for model_name,model in MODELS.items():
                if STOP.is_set() or time.time()>deadline-180: break
                jobs=[]
                for dataset,items in grouped.items():
                    previous=[r for r in rows if r['model']==model and r['dataset']==dataset and not r.get('excluded')]
                    if phase>=2 and not extend(previous):
                        skipped.append({'phase':phase,'model':model_name,'dataset':dataset,'reason':'earlier_results_floor_ceiling_or_unavailable'})
                        continue
                    selected=items[start:end]
                    if args.limit_per_dataset: selected=selected[:args.limit_per_dataset]
                    for index,case in enumerate(selected,start):
                        seed=202609140000+phase*100000+index*10
                        arms=['direct','summary','facts']+(['calculate'] if dataset=='finqa' else [])
                        for arm in arms: jobs.append((case,arm,seed,chunks))
                # Interleave datasets by case index; keep comparisons predetermined.
                jobs.sort(key=lambda j:(j[2],j[0]['dataset'],j[1]))
                model_output=output/'models'/model_name
                finished={r['episode_id'] for r in rows}
                jobs=[j for j in jobs if runner.digest({'model':model,'case_id':j[0]['id'],
                    'case_digest':runner.digest(j[0]),'arm':j[1],'seed':j[2],'chunks':j[3]})[:24] not in finished]
                if not jobs: continue
                process=None; client=None; service_folder=output/'services'/f'{invocation}-phase{phase}-{model_name}'
                try:
                    tokenizer=AutoTokenizer.from_pretrained(model,local_files_only=True,trust_remote_code=False)
                    process,log,helper=service(model,service_folder,deadline)
                    client=runner.Client(tokenizer,'http://127.0.0.1:18731',model,model_output,deadline)
                    snapshot(output/'STATUS.json',{'state':'running','phase':phase,'model':model_name,'queued':len(jobs),'returned':0,'updated':time.time()})
                    def one(job):
                        if STOP.is_set() or client.stop.is_set() or time.time()>=deadline-120: return None
                        return runner.episode(client,*job)
                    # Only four cases in flight; don't enqueue an entire failed-service backlog.
                    with ThreadPoolExecutor(max_workers=4) as pool:
                        for position in range(0,len(jobs),4):
                            if STOP.is_set() or client.stop.is_set() or process.poll() is not None or time.time()>=deadline-120: break
                            futures=[pool.submit(one,j) for j in jobs[position:position+4]]
                            for future in as_completed(futures):
                                result=future.result()
                                if result is not None: rows.append(result)
                            snapshot(output/'STATUS.json',{'state':'running','phase':phase,'model':model_name,
                                'done_in_phase':min(position+4,len(jobs)),'queued':len(jobs),
                                'returned':client.returned,'transport_errors':client.errors,'last_return':client.last_return,
                                'updated':time.time(),'deadline':deadline,'summary':summary(rows)})
                            if client.returned==0 and client.errors: client.stop.set()
                            if time.time()-client.last_return>90 and client.errors: client.stop.set()
                            if (output/'STOP').exists(): STOP.set()
                    runner.save(service_folder/'SCIENCE.json',{'returned':client.returned,'transport_errors':client.errors,
                        'last_return':client.last_return,'stopped_faulty':client.stop.is_set(),'ended':time.time()})
                except Exception as error:
                    failures.append({'phase':phase,'model':model_name,'error':f'{type(error).__name__}: {error}'})
                finally:
                    if process is not None:
                        if client is not None: client.stop.set()
                        helper._stop(process); log.close()
                        runner.save(service_folder/'RELEASED.json',{'pid':process.pid,'returncode':process.returncode,'released':time.time()})
                snapshot(output/'SUMMARY.json',{'updated':time.time(),'groups':summary(rows),'failures':failures,'skipped':skipped})
                if args.pilot_only: break
            if STOP.is_set() or time.time()>=deadline-180: break
    finally:
        snapshot(output/'STATUS.json',{'state':'stopped' if STOP.is_set() else 'finished',
            'updated':time.time(),'deadline':deadline,'summary':summary(rows),'failures':failures,'skipped':skipped})
        runner.save(output/f'TERMINAL-{invocation}.json',{'ended':time.time(),'owner_finished':True,
            'stop_requested':STOP.is_set(),'deadline_reached':time.time()>=deadline-180,'failures':failures})
        fcntl.flock(lock,fcntl.LOCK_UN); lock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',type=Path,default=ROOT/'data/cases-v2.jsonl')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--hours',type=float,default=36)
    parser.add_argument('--pilot-only',action='store_true')
    parser.add_argument('--limit-per-dataset',type=int,default=0)
    execute(parser.parse_args())
