"""One parent-launched train→initial/final native readout, owned service release in finally."""
import argparse
import ast
import copy
import os
import subprocess
import time
from pathlib import Path
import study as s
import native as n

def dependencies():
    suite=s.load('interface_pinned_suite',s.ROOT.parent/'leaf-post-sft-suite-v1/suite.py','6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1')
    path=s.ROOT.parent/'root-seed-lifecycle-continuation-v1/driver.py'
    s.check(path,'bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd')
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='observe_or_absent')
    scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
    original=suite.life.v1.process_identity
    suite.life.v1.process_identity=lambda pid:scope['observe_or_absent'](original,pid)
    return suite

def execute(output):
    started=time.time();deadline=started+3300;work_deadline=deadline-120
    ready=s.read(s.ROOT/'READY.json')
    for path,sha in ready['source_sha256'].items():s.check(path,sha)
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or ',' in os.environ['CUDA_VISIBLE_DEVICES']:raise ValueError('parent assigns one free GPU')
    output.mkdir(parents=True,exist_ok=False);suite=dependencies();suite.life.install()
    s.write(output/'RUN.json',dict(started_epoch=started,deadline_epoch=deadline,work_deadline_epoch=work_deadline,ready_sha256=s.sha(s.ROOT/'READY.json'),gpu=os.environ['CUDA_VISIBLE_DEVICES']))
    error=None;stages=[]
    try:
        argv=[str(s.TRAIN),str(s.ROOT/'train.py'),'run','--output',str(output/'training')]
        s.write(output/'TRAIN_COMMAND.json',dict(argv=argv,cap_seconds=900))
        with (output/'training.log').open('x') as log:
            process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            observation=suite.life.observe(process.pid)
            if observation is None:raise RuntimeError('training child identity unavailable')
            s.write(output/'TRAIN_PROCESS.json',suite.life.safe_observation(observation))
            try:
                code=process.wait(timeout=min(900,work_deadline-time.time()))
                if code:raise RuntimeError('training nonzero; preserved log/checkpoints')
            finally:suite.stop_child(process,suite.life.safe_observation(observation))
        result=s.read(output/'training/RESULT.json')
        for weight in ('initial','final'):
            stage=output/weight;stage.mkdir()
            binding=n.initial_binding()
            if weight=='final':
                old=binding['role_map']['root'];new='strict-rlm-qwen3-4b-root-interface-final4-v1'
                binding['models'].pop(old)
                selected=result['selected']
                binding['models'][new]=dict(path=selected['checkpoint'],adapter_sha256=selected['adapter_sha256'],config_sha256=selected['config_sha256'])
                binding['role_map']['root']=new
                binding['campaign_policy']={**binding['models'][new],'step':4,'optimizer_sha256':result['files_sha256']['optimizer.pt'],'rng_sha256':result['files_sha256']['rng_state.pt'],'state_sha256':selected['state_sha256']}
                binding['campaign_id']=s.ROOT.name
                binding['selected_epoch']=2
                binding.pop('receipt_uptake_study',None)
                binding['root_interface_sft_study']=s.ROOT.name
                binding['selection_path']=str(output/'training/SELECTION.json');binding['selection_sha256']=s.sha(output/'training/SELECTION.json')
                binding['selection_semantics']='fixed-final4; starting473210; fresh Adam; no validation selection'
            try:
                suite.start_service(stage,binding,min(work_deadline,time.time()+180))
                argv=[str(s.NATIVE),str(s.ROOT/'evaluate.py'),'--binding',str(stage/'BINDING.json'),'--endpoint',str(stage/'service/endpoint-original.json'),'--weight',weight,'--training',str(output/'training'),'--output',str(stage/'rollout'),'--deadline',str(min(work_deadline,time.time()+900))]
                suite.command(stage,'collect',argv,930,work_deadline)
                stages.append(dict(weight=weight,terminal=s.read(stage/'rollout/TERMINAL.json')))
            finally:suite.release_service(stage)
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
    terminal=dict(complete=error is None,error=error,stages=stages,elapsed_seconds=time.time()-started,deadline_epoch=deadline)
    s.write(output/'TERMINAL.json',terminal);return terminal

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');args=p.parse_args()
    result=execute(args.output);print(result);raise SystemExit(0 if result['complete'] else 1)
