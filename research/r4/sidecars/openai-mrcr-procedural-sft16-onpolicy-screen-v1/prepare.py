"""Freeze source/input READY, exercise actual CPU entry/native seams, gate owner on receipt."""
import json
import os
from pathlib import Path
import subprocess
import time
import checkpoint
import study

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    assert not study.READY.exists() and not (study.ROOT/'CPU_TESTS.json').exists()
    report=study.prepare_inputs();cp=checkpoint.seal();hook=study.terminal_hooks().qualify()
    original=study.read(study.ORIGINAL/'CPU_READY_V4.json')
    terminal=study.read(study.TERMINAL_HOOK/'CPU_READY.json')
    closure={**terminal['closure_sha256'],**original['closure_sha256']}
    paths=[*study.ROOT.glob('*.py'),study.ROOT/'QUESTION.md',study.ROOT/'RUNBOOK.md',checkpoint.RECEIPT,
           study.ORIGINAL/'CPU_READY_V4.json',checkpoint.SOURCE.RECEIPT,
           *[p for p in study.INPUTS.rglob('*') if p.is_file()],
           *[checkpoint.CHECKPOINT/n for n in cp['files_sha256']],checkpoint.CHECKPOINT/'STEP_COMMIT.json']
    for p in paths:closure[str(p)]=study.sha(p)
    for p,h in closure.items():assert study.sha(Path(p))==h,p
    ready={'schema':'fixed-cp16-g4-screen-ready-v1','created_epoch':time.time(),'arm':'checkpoint16','selected_step':16,
           'source_run_fixed_primary_step':32,'inputs':report,'sampling':original['sampling'],
           'terminal_condition':{'name':'terminal-strip-disabled','contract':hook},
           'caps_seconds':original['caps_seconds'],'checkpoint_receipt_sha256':study.sha(checkpoint.RECEIPT),
           'source_cp32_ready_sha256':study.sha(study.ORIGINAL/'CPU_READY_V4.json'),
           'output':str(study.ROOT/'outputs/attempt-001'),'closure_sha256':closure,'auto_launch':False,
           'optimizer_steps':0,'CPU_admission_requires':'CPU_TESTS.json returncode0,2passes and exact READY hash'}
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    argv=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_screen.py','--basetemp',str(study.ROOT/'cpu-001')]
    started=time.time();r=subprocess.run(argv,cwd=study.ROOT,capture_output=True,text=True,timeout=420)
    receipt={'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.time()-started,
             'tests_passed':2 if r.returncode==0 else None,'ready_sha256':study.sha(study.READY),'GPU_calls':0,
             'first_red':'two assertions failed because cp16 collector absent; no implementation existed',
             'fixture_sha256':{str(p):study.sha(p) for p in (study.ROOT/'cpu-001').rglob('*.json')}}
    study.write_x(study.ROOT/'CPU_TESTS.json',receipt)
    assert r.returncode==0,r.stdout+r.stderr
    import owner
    assert owner.verify()['identity']==ready['identity']
    print(json.dumps({'READY_sha256':study.sha(study.READY),'identity':ready['identity'],'pins':len(closure),
                     'CPU_TESTS_sha256':study.sha(study.ROOT/'CPU_TESTS.json'),'tests':r.stdout},sort_keys=True))

if __name__=='__main__':main()
