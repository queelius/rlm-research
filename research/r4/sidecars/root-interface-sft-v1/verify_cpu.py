"""Record focused test commands/stdout without model calls."""
import subprocess
import os
import study as s

def run():
    commands=[['native',str(s.NATIVE),'-m','pytest','-q',str(s.ROOT/'tests/test_contract.py'),str(s.ROOT/'tests/test_dispatch.py')],['training',str(s.TRAIN),'-m','pytest','-q',str(s.ROOT/'tests/test_train.py')]]
    results=[]
    for name,*argv in commands:
        p=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'},text=True,capture_output=True)
        results.append(dict(name=name,argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        if p.returncode:raise ValueError(results)
    s.write(s.ROOT/'CPU_TESTS.json',dict(status='PASS',results=results,red_evidence='test_contract.py failed collection with missing study; test_train.py failed collection with missing train before implementations. Terminal tool outputs retained in preparation session; no fabricated red stdout.',gpu_calls=0))
    print('PASS native4 + real PEFT1 focused tests')

if __name__=='__main__':run()
