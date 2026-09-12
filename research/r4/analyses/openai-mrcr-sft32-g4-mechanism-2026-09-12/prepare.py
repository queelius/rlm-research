"""Seal the small read-only G4 analyzer with focused CPU evidence."""
import os
import subprocess
import time
from pathlib import Path
import analyze as a

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'READY.json').exists()
    desc=a.read(a.ROOT/'SOURCE.json');source=a.read(desc['ready'])
    assert a.sha(desc['ready'])==desc['ready_sha256'] and source['identity']==desc['identity']
    proof=a.read(a.ROOT/'ENTRY_REVIEW.json');assert proof['status']=='PASS' and not proof['verify_ready_mocked']
    native='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'
    argv=[native,'-m','pytest','-q','-p','no:cacheprovider','test_analyze.py']
    t=time.time();test=subprocess.run(argv,cwd=a.ROOT,capture_output=True,text=True,timeout=90)
    assert test.returncode==0,test.stdout+test.stderr
    a.write(a.ROOT/'CPU.json',{'argv':argv,'returncode':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
        'elapsed_seconds':time.time()-t,'GPU_calls':0,'new_model_queries':0,
        'actual_archived_native_fixture':True,'entry_proof_sha256':a.sha(a.ROOT/'ENTRY_REVIEW.json')})
    hooks=a.STORE/'sidecars/openai-mrcr-procedural-sft-terminal-strip-disabled-v1/CPU_READY.json'
    closure={**a.read(hooks)['closure_sha256'],**source['closure_sha256']}
    for p in [Path(desc['ready']),Path(desc['binding_source']),hooks,
              a.STORE/'sidecars/openai-mrcr-procedural-sft-warmstart-v1/TEACHER_CORPUS_V2.json',
              *a.ROOT.glob('*.py'),a.ROOT/'RUNBOOK.md',a.ROOT/'SOURCE.json',a.ROOT/'CPU.json',a.ROOT/'ENTRY_REVIEW.json']:
        closure[str(p)]=a.sha(p)
    fixture=a.STORE/'sidecars/openai-mrcr-procedural-sft-terminal-strip-disabled-v1/cpu-green-002'
    for p in fixture.rglob('*.json'):
        if p.name in ('DERIVED.json','EPISODE.json') or p.name.endswith('-result.json'):
            closure[str(p)]=a.sha(p)
    for p,h in closure.items():assert a.sha(p)==h,p
    value={'schema':'cp32-g4-mechanism-analyzer-ready-v1','created_epoch':time.time(),
        'source_READY_sha256':desc['ready_sha256'],'output':desc['output'],'closure_sha256':closure,
        'planned_groups':8,'group_size':4,'planned_episodes':32,'one_check_no_polling':True,
        'fixed_argv':[native,str(a.ROOT/'analyze.py'),'check'],'GPU_calls':0,'optimizer_steps':0}
    value['identity']=a.digest(value);a.write(a.ROOT/'READY.json',value);a.verify()
    print({'READY_sha256':a.sha(a.ROOT/'READY.json'),'identity':value['identity'],'pins':len(closure),'tests':test.stdout})

if __name__=='__main__':main()
