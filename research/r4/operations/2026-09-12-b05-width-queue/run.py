"""MAIN admits fixed helper fan-out; launch under external coordinator flock."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('width_lease_helpers',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'b05-helper-width-v1'
EXPECTED='117837ff4d26f93b533f9cf15a589ebbe6514fb3d75aa2dcd9f0b1a2dde22a81'

def execute():
    ready_path=SIDE/'READY_RUN.json';assert driver.sha(ready_path)==EXPECTED
    ready=driver.read(ready_path);driver.verify_closure(ready)
    assert ready['planned_calls']==126 and ready['cases']==9 and ready['helpers']==[1,2,4]
    previous=driver.SIDES/'finqa-scalar-vs-dsl-v1/outputs/attempt-001/OWNER_TERMINAL.json'
    assert driver.read(previous)['released']
    driver.empty_gpu();assert not (SIDE/'outputs/attempt-001').exists()
    command=ready['argv']
    assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner.py'),'run','--outer-seconds','700']
    driver.write_once('START.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,
        question='Does smaller helper input improve eligible-ID selection at fixed total output budget?',
        units='9 fresh stages,3/width6,12,20;2 fixed decodes each;fixed1/2/4helpers',
        metric='Primary strict exactness with invalid/unknown separate; paired outcomes and physical tokens. Unordered set diagnostic posthoc, not primary repair.',
        review='MAIN read runner, collector, metrics, preparation/tests, outcome-blind partition source and design. Two fixtures passed,14 actual native HTTP requests; real owner verify reached CPU guard.',
        caps=dict(science=600,owner=700,external=800),
        seed_policy='202609310000+100*case+10*repeat+part;T.5;384/192/96 tokens perhelper',
        checkpoint_policy='Fixed released4B, each native request/response saved, no retries or outcome-based stopping',
        limitations='Candidate generator with planted feasibility; fixed fan-out, not learned delegation or recursive depth; sorting contract may reject semantically meaningful sets',
        predecessor_sha256=driver.sha(previous),external_flock=True,command=command))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','800',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=SIDE/'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
