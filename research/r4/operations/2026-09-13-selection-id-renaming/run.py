"""MAIN admits a fixed public-ID renaming mechanism probe, not new training."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('renamed_selection_lease',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'b05-selection-id-renaming-v1'
EXPECTED='f3edb927b6ecafc988a767b19cc060365b15186002f19aa3e247a8c55bb5ca58'

def execute():
    previous=ROOT.parent/'2026-09-13-selection-dose10/QUEUE_TERMINAL.json'
    assert previous.exists();driver.empty_gpu()
    path=SIDE/'READY.json';assert driver.sha(path)==EXPECTED
    ready=driver.read(path);driver.verify_closure(ready)
    assert ready['planned']['total']==36 and not ready['mapping_used_outcomes_or_gold']
    assert not (SIDE/'outputs/attempt-001').exists()
    command=ready['argv']
    assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner.py'),'run','--outer-seconds','700']
    driver.write_once('ADMISSION.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,external_flock=True,
        question='Does the smaller selection update retain its local advantage after every implementation ID is consistently renamed?',
        comparison='Original9 trainingstages×2sameseeds, genuinebase vs ORIGINAL LR1e-4cp1, notnewdose10; unchangedpublicfacts, reversiblepublicbijection, hostlabelsremappedseparately',
        metric='Strict exact and unordered semantic/BA with validdenominators; pairedall36 nativecost and unavailable/invalidseparate',
        review='MAIN read all430 source lines+QUESTION, inherited72 owner and actualcollector; publicinverse restores exactprompts and unchangedfacts; nativeHTTP fixture and fullownersealverify passed.',
        seeds='Originaltrainingseeds/T.5/384output/4workers; samecurrentdualLoRA runtime',
        checkpoint_policy='No optimizer/selection; originalcp1fixed, eachnativecall persisted, noeligibilityrepair',
        caps_seconds=dict(science=600,owner=700,external=800),
        limitations='Withintrainingstructureprobe; root/stageIDs unchanged, implementationtokenization changes, notpurecausal ornewtaskgeneralization proof',
        predecessor_sha256=driver.sha(previous),command=command))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','800',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=SIDE/'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
