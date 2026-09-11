"""Four candidate windows, zero-to-four real Adam updates, one owned clock."""
import argparse
import functools
import os
import signal
import subprocess
import time
import traceback
import uuid
from pathlib import Path
import collect
import common
import export
import native as n
import study as s
import windows

@functools.lru_cache(maxsize=1)
def dependencies():
    old=s.private('coordinator.py',{'study':s,'native':n,'common':common,'collect':collect,'export':export})
    return old.dependencies()[0]

def group_cap(cutoff,now=None):
    remaining=cutoff-(time.time() if now is None else now)
    if remaining<=300:raise TimeoutError('no complete group/save allowance before final reserve')
    return min(300,remaining-300)

def optimizer_budget(cutoff,now=None):
    now=time.time() if now is None else now
    if cutoff-now<120:raise TimeoutError('less than120s optimizer/save allowance')
    return min(240,cutoff-now-60)

def stage(directory,phase,service,deadline,cap,generation=None):
    directory.mkdir(parents=True,exist_ok=False)
    spec=directory/'CAPTURE_SPEC.json'
    collect.prepare_spec(phase,service/'BINDING.json',service/'service/endpoint-original.json',spec,cap,generation)
    argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'--spec',str(spec),'--output',str(directory/'rollout'),'--deadline',str(min(deadline,time.time()+cap))]
    dependencies().command(service,'collect-'+phase,argv,min(cap+15,max(.001,deadline-time.time())),deadline)
    result=export.export_attempt(directory/'rollout',directory/'export')
    if result['integrity_failures']:raise ValueError('native integrity failure; retain exact NULLs, no admission change')
    return result

def train_window(directory,generation,cutoff):
    suite=dependencies();cap=optimizer_budget(cutoff)
    argv=[str(s.TRAIN),str(s.ROOT/'train.py'),'--group',str(directory/'union/GROUP.json'),
          '--generation',str(directory/'GENERATION.json'),'--output',str(directory/'training'),
          '--deadline',str(time.time()+cap)]
    s.write(directory/'TRAIN_COMMAND.json',{'argv':argv,'forward_backward_cap_seconds':cap,'checkpoint_release_allowance':60,'started_epoch':time.time()})
    with (directory/'training.log').open('x') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        observed=suite.life.observe(process.pid)
        if observed is None:raise RuntimeError('trainer exited before owned observation')
        owner=suite.life.safe_observation(observed);s.write(directory/'TRAIN_OWNER.json',owner)
        try:
            if process.wait(timeout=min(cap+60,max(.001,cutoff-time.time())))!=0:raise RuntimeError('owned trainer nonzero; no retry')
        finally:
            suite.stop_child(process,owner);s.write(directory/'TRAIN_EXIT.json',{'returncode':process.returncode,'ended_epoch':time.time()})
    return common.c.checkpoint_policy(directory/'training',generation)

def execute(output):
    started=time.time();m=s.verify_prepared();_,_,initial=common.starting_decision();suite=dependencies()
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must assign sole owned GPU')
    output.mkdir(parents=True,exist_ok=False)
    cutoff,deadline,inclusive=started+2820,started+3480,started+3600
    s.write(output/'RUN.json',{'campaign_id':m['campaign_id'],'campaign_sha256':s.sha(s.ROOT/'CAMPAIGN.json'),
        'started_epoch':started,'training_cutoff_epoch':cutoff,'work_deadline_epoch':deadline,'inclusive_deadline_epoch':inclusive,
        'gpu':gpu,'starting_policy':initial,'starting_binding_sha256':s.sha(s.ROOT/'START.json'),
        'automatic_resume':False,'max_training_attempts':128,'readout_attempts':48})
    def expired(_signal,_frame):raise TimeoutError('3600 inclusive envelope or parent signal')
    for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):signal.signal(sig,expired)
    signal.setitimer(signal.ITIMER_REAL,max(.001,inclusive-time.time()))
    policy=initial;service=None;completed=0;training_attempts=0;readouts={};results=[]
    def release():
        nonlocal service
        if service is not None:
            suite.release_service(service)
            service=None
    def ensure_service(boundary):
        nonlocal service
        if service is None:
            service=output/'services'/f'step-{policy["step"]:02d}-{uuid.uuid4().hex[:8]}'
            service.mkdir(parents=True)
            suite.start_service(service,collect.binding_for(policy),min(boundary,time.time()+180))
        return service
    try:
        baseline_end=min(deadline,started+660)
        ensure_service(baseline_end)
        readouts['before']=stage(output/'readout-before','readout-before',service,baseline_end,min(480,baseline_end-time.time()))
        for window in range(1,5):
            # Between completed windows, insufficient time selects the last real
            # checkpoint. Inside a sampled window, a cap is a retained STOP.
            if cutoff-time.time()<=480:break
            directory=output/f'window-{window:02d}';directory.mkdir()
            g=common.generation(window,policy);s.write(directory/'GENERATION.json',g)
            ensure_service(cutoff-300)
            flags=[];paths=[]
            while windows.needs_group(flags):
                group=len(flags)+1;cap=group_cap(cutoff)
                folder=directory/f'group-{group}'
                r=stage(folder,f'window-{window}-group-{group}',service,cutoff-300,cap,g)
                training_attempts+=r['recorded'];flags.append(r['training_group_episodes']>0);paths.append(folder/'export')
            union=export.export_union(paths,g,directory/'union')
            new=None
            if any(flags):
                release()
                if not suite.life.v1.ports_free():raise ValueError('owned service remains before optimizer')
                new=train_window(directory,g,cutoff)
            cursor=windows.transition(completed,policy,window,flags,new)
            completed=cursor['completed_windows'];policy=cursor['policy']
            record={**cursor,'generation':g,'union_manifest_sha256':s.sha(directory/'union/MANIFEST.json'),
                    'mandatory_first_two_mixed_groups':sum(flags[:2]),'consumed_mixed_groups':sum(flags),
                    'consumed_groups':len(flags),'training_attempts':union['recorded'],
                    'selected_episodes':union['training_group_episodes'],'ended_epoch':time.time()}
            s.write(directory/'WINDOW_RESULT.json',record);results.append(record)
        selection={'rule':'last committed policy after completed windows or between-window cutoff; no validation selection',
                   'selected_step':policy['step'],'policy':policy,'completed_candidate_windows':completed}
        s.write(output/'SELECTION.json',selection)
        ensure_service(deadline)
        readouts['after']=stage(output/'readout-after','readout-after',service,deadline,min(480,deadline-time.time()))
        release()
        result={'status':'complete','selection':selection,'optimizer_steps':policy['step'],
                'candidate_windows':results,'training_attempts':training_attempts,'maximum_training_attempts':128,
                'readouts':readouts,'planned_readout_episodes':48,'training_candidates_unrun':128-training_attempts,
                'elapsed_seconds':time.time()-started,'owned_service_released':True}
        s.write(output/'FINAL.json',result);return result
    except BaseException as error:
        # A checkpoint state is an atomic commit even if a later boundary fails.
        commits=[]
        for path in sorted(output.glob('window-*/training/checkpoint-*/state.json')):
            g=s.read(path.parents[1].parent/'GENERATION.json')
            commits.append(common.c.checkpoint_policy(path.parents[1],g))
        if commits:policy=max(commits,key=lambda p:p['step'])
        s.write(output/('STOP-'+uuid.uuid4().hex+'.json'),{'status':'stopped','type':type(error).__name__,
            'reason':str(error),'optimizer_steps':policy['step'],'last_policy':policy,
            'completed_candidate_windows':completed,'completed_group_attempts':training_attempts,
            'elapsed_seconds':time.time()-started,'traceback':traceback.format_exc(),'later_readout_status':'unrun unless recorded'})
        raise
    finally:
        try:release()
        finally:signal.setitimer(signal.ITIMER_REAL,0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001');a=p.parse_args()
    print({'campaign_id':s.verify_prepared()['campaign_id'],'gpu_calls':0} if a.command=='verify' else execute(a.output.resolve()))
