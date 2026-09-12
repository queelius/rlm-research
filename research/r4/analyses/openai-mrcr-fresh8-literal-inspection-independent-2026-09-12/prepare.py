"""Seal the thin CPU analyzer; do not check or poll experiment completion here."""
import os
from pathlib import Path
import subprocess
import time
import analyze as a


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'CPU_READY.json').exists()
    assert a.core.sha(a.SIDE/'READY.json')==a.SIDE_SHA and a.core.sha(a.OLD_AUDIT)==a.OLD_SHA
    side=a.core.read(a.SIDE/'READY.json');old=a.core.read(a.OLD_AUDIT)
    closure={**side['closure_sha256'],**old['source_sha256']}
    for p,w in closure.items():assert a.core.sha(p)==w,p
    command=['/project/alex_phd/envs/prime-rl-5990b1b/bin/python','-m','pytest','-q','-p','no:cacheprovider','test_audit.py']
    run=subprocess.run(command,cwd=a.ROOT,capture_output=True,text=True,timeout=120)
    a.core.write(a.ROOT/'CPU_TESTS.json',{'argv':command,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,
        'scope':'Inert synthetic ordering/ambiguity/invalid-code/exact-whitespace checks and one real saved native control decode plus both study bindings; no GPU.'})
    assert run.returncode==0,run.stdout+run.stderr
    paths=[*a.ROOT.glob('*.py'),a.ROOT/'RUNBOOK.md',a.ROOT/'CPU_TESTS.json',a.SIDE/'READY.json',a.OLD_AUDIT,a.CORE]
    closure.update({str(p):a.core.sha(p) for p in paths})
    ready={'schema':'literal-inspection-independent-cpu-ready-v1','created_epoch':time.time(),'sidecar_ready_sha256':a.SIDE_SHA,
        'cached_control_audit_sha256':a.OLD_SHA,'closure_sha256':closure,'GPU_calls':0,'planned_pairs':32,'paired_context_units':8,
        'unknown_not_wrong':True,'inspection_candidates_require_manual_adjudication':True,'one_check_then_stop':True,
        'fixed_argv':[command[0],str(a.ROOT/'analyze.py'),'check','--output',str(a.ROOT/'outcome-001')]}
    ready['identity']=a.core.digest(ready);a.core.write(a.ROOT/'CPU_READY.json',ready)
    print({'CPU_READY_sha256':a.core.sha(a.ROOT/'CPU_READY.json'),'identity':ready['identity'],'closure_files':len(closure),'tests':run.stdout})


if __name__=='__main__':main()
