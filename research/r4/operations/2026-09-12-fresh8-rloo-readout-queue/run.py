"""MAIN admits all three fixed RLOO readouts, independent of interim scores."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('fresh8rloo_readout_lease_helpers',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'openai-mrcr-cp32-fresh8-final-rloo-eval-v1'
READY=SIDE/'READY.json'
EXPECTED='5bb409be9a59601772527b052c28d445809b3e0eeb3d40ea6d33a2684de0028c'

def execute():
    assert driver.sha(READY)==EXPECTED
    ready=driver.read(READY);driver.verify_closure(ready);driver.empty_gpu()
    assert ready['planned']==64 and ready['all_phases_regardless_score']
    driver.write_once('ADMISSION.json',dict(authority='MAIN',epoch=time.time(),ready_sha256=EXPECTED,
        ready_identity=ready['identity'],wrapper_sha256=driver.sha(__file__),
        review='MAIN read all381 source/test/preparation lines and RUNBOOK. Actual owner verification qualifies cp32 initial tensors, new cp1/Adam/RNG,12 replay and20 zero skips; two focused actual-input/sampler/replay fixtures passed. Native collector seam unchanged.',
        question='Does a final-only RLOO step using fresh mixed-reward groups improve delivery across short, longer and higher-ordinal contexts?',
        phases=['held','long','fourneedle'],units='16 contexts per panel; short has2 seeds, other panels1;64 outputs not64 independent contexts',
        metrics='Raw exact, availability, clean retrieval, final failure categories, paired context outcomes and physical native usage',
        seed_policy='Exact sealed schedules: short fresh replica202609270000..31; original long/fourneedle seeds, T.5/2048/six total actions',
        checkpoint_policy='One fixed already completed cp1; persist each native return/episode; no outcome gate or further optimizer',
        baseline_policy='Qualified new replica cp32/fixedRL short controls and existing long/fourneedle cp32; source batch AND baseline differ versus fixedRL'))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    private=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')
    env['STRICT_RLM_CALIBRATION_API_KEY']=private['vllm']['api_key'][0]
    completed=[]
    for phase in ('held','long','fourneedle'):
        driver.empty_gpu();command=ready['fixed_argv'][phase]
        assert command==[str(driver.STORE.parent.parent/'envs/prime-rl-5990b1b/bin/python'),str(SIDE/'owner.py'),'run','--phase',phase]
        output=SIDE/f'outputs/{phase}-001';assert not output.exists()
        cap=ready['caps'][phase]['external']
        driver.write_once(phase+'-START.json',dict(epoch=time.time(),command=command,external_seconds=cap))
        with (ROOT/(phase+'-owner.log')).open('x') as log:
            result=subprocess.run(['timeout','--signal=TERM','--kill-after=30',str(cap),*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
        terminal=output/'OWNER_TERMINAL.json'
        assert terminal.exists() and driver.read(terminal).get('released'), 'owned service release required before next panel'
        row=dict(phase=phase,returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal))
        driver.write_once(phase+'-EXIT.json',dict(epoch=time.time(),**row));completed.append(row)
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),phases=completed))

if __name__=='__main__':execute()
