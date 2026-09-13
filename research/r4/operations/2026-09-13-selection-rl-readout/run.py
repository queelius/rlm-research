"""MAIN admits fixed base/cp1 train and held selection readout under flock."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('selection_readout_lease',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'b05-flat-selection-rl-eval-v1'
EXPECTED='a32cae2ac08ec93327805eef6afc886e8f15e20fd00361bff90488db614b2d52'

def execute():
    previous=ROOT.parent/'2026-09-13-selection-rl-and-fresh-finqa/QUEUE_TERMINAL.json'
    assert previous.exists();driver.empty_gpu()
    path=SIDE/'READY.json';assert driver.sha(path)==EXPECTED
    ready=driver.read(path);driver.verify_closure(ready)
    assert ready['planned_calls']==72 and ready['all_phases_regardless_score']
    assert not (SIDE/'outputs/attempt-001').exists()
    command=ready['argv']
    assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner.py'),'run','--outer-seconds','700']
    driver.write_once('ADMISSION.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,
        question='Does one reward update on actual eligible-ID selections improve trained and new stage problems?',
        comparison='Genuine released base versus sole fixed BA18 step1; both train18 and freshheld18, paired seeds/prompts/T.5/384,4workers',
        metric='Strict ordered exact primary, unordered semantic exact/BA/confusion secondary, all18 denominators and unavailable/invalid separate',
        review='MAIN read all359 newPythonlines, inherited Collector.call and RUNBOOK; two focused fixtures, actual current-service binding, full cp1 tensor/Adam/replay and real owner CUDA-hidden guard passed.',
        caps_seconds=dict(science=600,owner=700,external=800),
        checkpoint_policy='No optimizer/checkpoint selection; each raw native request/response/usage persisted, only fixedcp1',
        limitations='Nine held stages/two paireddecodes, same candidate taskfamily. Current sharedLoRA service differs from older widthservice; no poolingoldbasecontrols or batchinvariance claim. StoredFP32 adapter servedBF16.',
        external_flock=True,predecessor_sha256=driver.sha(previous),
        prior_optional8B_failure='Owned orphan explicitly stopped; old failedterminal unchanged, CLEANUP.md in2026-09-13-b05-alternative-model',
        command=command))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','800',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=SIDE/'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
