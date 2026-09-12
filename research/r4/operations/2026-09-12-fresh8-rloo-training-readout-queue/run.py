"""MAIN admits one fixed in-sample readout, with no new optimizer step."""
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
import hashlib
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('trainread_lease_helpers',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'openai-mrcr-cp32-fresh8-final-rloo-train-readout-v1'
EXPECTED='8f035e96a8bcf26a1a4a7219aabfdd0f9ed2fab2f0fe965a8f5426c02ca41827'

def execute():
    ready_path=SIDE/'READY.json';assert driver.sha(ready_path)==EXPECTED
    ready=driver.read(ready_path);driver.verify_closure(ready);driver.empty_gpu()
    assert ready['planned']==32 and ready['all32_regardless_source_advantage']
    output=SIDE/'outputs/train-001';assert not output.exists()
    command=ready['fixed_argv']['train']
    assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner.py'),'run','--phase','train']
    driver.write_once('ADMISSION.json',dict(authority='MAIN',epoch=time.time(),ready_sha256=EXPECTED,
        ready_identity=ready['identity'],wrapper_sha256=driver.sha(__file__),
        review='MAIN read all159 new Python lines and RUNBOOK; actual original schedule/environment/qualified checkpoint CPU fixture passed. Reuses already reviewed native owner/collector.',
        question='Did final-only RLOO improve even its own original training rollouts, versus merely changing teacher-forced probabilities?',
        units='8 training contexts,4 original seeds each;32 outputs not independent contexts',
        metrics='Raw exact, paired outcomes, clean retrieval versus final copy errors, native costs and changed paths',
        seed_policy='Original202609250000..31;T.5/2048/six total actions/zero children',
        checkpoint_policy='Fixed cp1; every native response and episode saved; no optimizer or model selection',
        baseline_policy='Qualified original cp32 fresh8 control7/32; in-sample diagnostic, not generalization',
        external_seconds=1200))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','1200',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=output/'OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
