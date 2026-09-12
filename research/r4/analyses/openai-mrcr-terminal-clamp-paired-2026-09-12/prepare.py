"""Freeze this small analyzer after an actual archived-stage CPU check."""
import os
import subprocess
import time
import analyze as a

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not (a.ROOT/'READY.json').exists()
    source=a.read(a.SIDE/'CPU_READY.json');assert a.sha(a.SIDE/'CPU_READY.json')==a.READY_SHA
    native='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'
    argv=[native,'-m','pytest','-q','-p','no:cacheprovider','test_compare.py']
    test=subprocess.run(argv,cwd=a.ROOT,capture_output=True,text=True,timeout=30)
    assert test.returncode==0,test.stdout+test.stderr
    baseline=a.stage(a.OLD,False)
    assert baseline['available']==32 and baseline['returned_exact']==17
    assert baseline['physical']['returned']==66 and baseline['physical']['errors']==0
    a.write(a.ROOT/'BASELINE_CHECK.json',{k:v for k,v in baseline.items() if k!='rows'})
    a.write(a.ROOT/'CPU.json',{'argv':argv,'returncode':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
        'GPU_calls':0,'new_model_queries':0,'actual_full32_baseline_reader_passed':True,
        'first_red':'missing analyze module; then actual fixture exposed nullable tool_calls, fixed before seal'})
    closure=dict(source['closure_sha256']);closure[str(a.SIDE/'CPU_READY.json')]=a.READY_SHA
    for p in [*a.ROOT.glob('*.py'),a.ROOT/'RUNBOOK.md',a.ROOT/'CPU.json',a.ROOT/'BASELINE_CHECK.json']:
        closure[str(p)]=a.sha(p)
    for p,want in closure.items():assert a.sha(p)==want,p
    value={'schema':'terminal-clamp-paired-analyzer-ready-v1','created_epoch':time.time(),
        'closure_sha256':closure,'source_READY_sha256':a.READY_SHA,'old':str(a.OLD),'new':str(a.NEW),
        'CPU_sha256':a.sha(a.ROOT/'CPU.json'),'one_shot_no_polling':True,'planned':32,'context_units':16,
        'fixed_argv':[native,str(a.ROOT/'analyze.py'),'check'],'GPU_calls':0}
    value['identity']=a.digest(value);a.write(a.ROOT/'READY.json',value);a.verify()
    print({'READY_sha256':a.sha(a.ROOT/'READY.json'),'identity':value['identity'],'pins':len(closure),'test':test.stdout})

if __name__=='__main__':main()
