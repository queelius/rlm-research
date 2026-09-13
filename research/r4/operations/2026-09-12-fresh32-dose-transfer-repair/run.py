"""MAIN runs both fixed endpoints on untouched conversations under external flock."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('fresh32_lease_helpers',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'openai-mrcr-fourneedle-balanced32-transfer-eval-v1'
EXPECTED='284d965c6b23da9d17d2b319dbc798d44950347b9381b10d41fec2c67a33ced4'

def execute():
    path=SIDE/'RUN_READY_SERVICE_REPAIR.json';assert driver.sha(path)==EXPECTED
    ready=driver.read(path)
    driver.verify_closure({'closure_sha256':ready['authoritative_closure_sha256']})
    assert ready['both_arms_required_regardless_score']
    previous=driver.SIDES/'finqa-two-example-interface-v1/outputs/attempt-001/OWNER_TERMINAL.json'
    assert driver.read(previous)['released']
    driver.empty_gpu()
    driver.write_once('ADMISSION.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,
        question='Does the fixed larger RL update improve exact answer delivery on unused conversation contexts?',
        comparison='Original procedural cp32 versus LR1e-4 single update;32 new contexts8perordinal1-4; bothnewarms regardlessscore',
        metric='Raw exact answers; actual native paths/retrieval/copying/cost; unknown separate',
        seeds='202609270000+frozenrowindex;pairedT.5;2048/action;6totalturns;4workers',
        review='MAIN read scientific sources and observed service repair. Actual suite.start_service argv and both real bindings pass focused fixture; actual owner verifies botharms. Attempt001 zero-science failures preserved; repaired002 uses proven dual-LoRA wrapper.',
        closure_files=len(ready['authoritative_closure_sha256']),
        caps_seconds_per_arm=dict(science=900,owner=1100,external=1200),
        checkpoint_policy='Fixed checkpoints; each native call/episode persisted, no new optimizer or retries',
        limitations='Development-selected learning rate; new projectcontexts, samepublictaskfamily; not pretraining-clean or learneddecomposition evidence',
        external_flock=True,predecessor_sha256=driver.sha(previous)))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    phases=[]
    for arm in ('cp32','lr1e4'):
        driver.verify_closure({'closure_sha256':ready['authoritative_closure_sha256']});driver.empty_gpu()
        output=SIDE/'outputs'/f'{arm}-002';assert not output.exists()
        command=ready['fixed_argv'][arm]
        assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner_repair.py'),'run','--stage',arm,'--outer-seconds','1100']
        driver.write_once(arm+'-START.json',dict(epoch=time.time(),arm=arm,command=command))
        with (ROOT/(arm+'.log')).open('x') as log:
            result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','1200',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
        terminal=output/'OWNER_TERMINAL.json';assert terminal.exists() and driver.read(terminal).get('released')
        driver.empty_gpu()
        phases.append(dict(arm=arm,returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))
        driver.write_once(arm+'-TERMINAL.json',phases[-1])
    driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),phases=phases))

if __name__=='__main__':execute()
