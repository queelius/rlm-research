"""CPU-only old-RED/new-GREEN proof and immutable recovery authority handoff."""
import os
import subprocess
import time
from pathlib import Path
import recovery as r

def main():
    pack=r.science();s=pack.s
    tests=[]
    for label,old,extra in [('old-red',True,['-k','actual_main']),('new-green',False,[])]:
        env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
        env.pop('RECOVERY_EXPECT_OLD',None)
        if old:env['RECOVERY_EXPECT_OLD']='1'
        argv=[r.PYTHON,'-m','pytest','-q','test_recovery.py',*extra]
        result=subprocess.run(argv,cwd=r.ROOT,env=env,capture_output=True,text=True,timeout=60)
        if old:
            if result.returncode!=1 or '5d6aab04' not in result.stdout or '076e65b7' not in result.stdout:
                raise ValueError('old failure did not reproduce exact observed hash mismatch')
        elif result.returncode:raise ValueError('new focused tests failed: '+result.stdout)
        tests.append({'label':label,'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    s.write_once(r.ROOT/'CPU_TESTS.json',{'status':'PASS','old_red_expected':True,'tests':tests,'gpu_calls':0,'model_calls':0})
    old=r.SCIENCE/'owned/attempt-001';operation=r.ROOT.parent.parent/'operations/2026-09-09-after-coverage48-fresh96/attempt-001/fresh96'
    failed=[old/'ATTEMPT.json',old/'qwen3/ERROR.json',old/'qwen3/FINISH.json',old/'qwen3/SERVICE_REQUEST.json',
            old/'qwen3/service/SERVER_START.json',old/'qwen3/LAUNCHER_PROCESS.json',
            old/'qwen3/OWNED_PROCESSES/4119052-1077170473.json',operation/'EXIT.json',operation/'COMMAND.json']
    relation={'original_scientific_ready_sha256':r.ORIGINAL_READY_SHA,'old_failed_attempt':str(old),
        'failure_files_sha256':{str(p):s.sha(p) for p in failed},
        'observed_failure':'only launcher hash mismatch: inherited __file__ old path; start/release both refused; zero scientific client command',
        'new_owned_attempt':str(r.ROOT/'owned/attempt-001'),'scientific_outputs':str(r.SCIENCE/'outputs'),
        'outputs_absent_at_preparation':not (r.SCIENCE/'outputs').exists(),'same_frozen96_seeds_and_bodies':True,
        'separate_main_authorized_parent_budget_seconds':1800,'automatic_retry':False,'old_cleanup_authority':'MAIN only; no recovery cleanup of old attempt'}
    if not relation['outputs_absent_at_preparation']:raise ValueError('scientific outputs already exist')
    s.write_once(r.ROOT/'ATTEMPT_RELATION.json',relation)
    sources=dict(s.read(r.SCIENCE/'READY.json')['source_sha256'])
    sources[str(r.SCIENCE/'READY.json')]=r.ORIGINAL_READY_SHA
    local=list(r.ROOT.glob('*.py'))+list(r.ROOT.glob('*.md'))+[r.ROOT/'source/serve.py',r.ROOT/'CPU_TESTS.json',r.ROOT/'ATTEMPT_RELATION.json']
    sources.update({str(p):s.sha(p) for p in local});sources.update(relation['failure_files_sha256'])
    for path,want in sources.items():s.check(path,want)
    ready={'status':'CPU_READY_MAIN_ACCEPTANCE_REQUIRED','original_ready_sha256':r.ORIGINAL_READY_SHA,
        'source_sha256':sources,'old_failed_attempt':str(old),'recovery_relation_sha256':s.sha(r.ROOT/'ATTEMPT_RELATION.json'),
        'driver':str(r.ROOT/'owned.py'),'driver_sha256':s.sha(r.ROOT/'owned.py'),
        'launcher':str(r.ROOT/'source/serve.py'),'launcher_sha256':s.sha(r.ROOT/'source/serve.py'),
        'launch_argv':[r.PYTHON,str(r.ROOT/'owned.py'),'--directory',str(r.ROOT/'owned/attempt-001')],
        'verify_argv':[r.PYTHON,str(r.ROOT/'owned.py'),'--verify'],
        'completion_markers':[str(r.ROOT/'owned/attempt-001/TERMINAL.json'),str(r.SCIENCE/'outputs/qwen3/STATUS.json'),str(r.SCIENCE/'outputs/qwen35/STATUS.json')],
        'caps':{'work':1650,'owned':1770,'parent':1800},'gpu_calls':0,'model_calls':0,
        'source_paths':len(sources),'prepared_epoch':time.time(),'launch_authorized':False}
    s.write_once(r.ROOT/'READY.json',ready)
    r.verify()
    print({'ready_sha256':s.sha(r.ROOT/'READY.json'),'launcher_sha256':ready['launcher_sha256'],'source_paths':len(sources),'gpu_calls':0})

if __name__=='__main__':main()
