"""Finish the already-prepared fresh-instance/history replication under flock."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('fresh_normalization_lease',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'b05-public-normalization-fresh12-v1'
EXPECTED='109f3f0e1ea54bc53dbb0dd52a9544cd97e8292d15c0851f04e5e6c43992f5c0'

def execute():
    previous=ROOT.parent/'2026-09-13-selection-dose10-readout/QUEUE_TERMINAL.json'
    assert previous.exists();driver.empty_gpu()
    path=SIDE/'CPU_READY.json';assert driver.sha(path)==EXPECTED
    ready=driver.read(path);driver.verify_closure(ready)
    assert ready['planned_physical_calls']==48 and ready['all_new_stages_and_new_raw_controls']
    assert not (SIDE/'outputs/attempt-001').exists()
    command=ready['argv']
    assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner.py'),'run','--outer-seconds','700']
    driver.write_once('ADMISSION.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,external_flock=True,
        question='Does fixed public normalization improve selection on unused stages and greater applied-change history?',
        comparison='12newcontexts; sixhistory1 widths6/12/20 and sixhistory3 widths6/12; bothraw/normalized freshbase, two pairedseeds, checkrevisionsfixed1',
        metric='Unordered exact primary, strictformatseparate; perhistory/width/context BA/confusion with explicitvaliddenominators and physicalcost',
        review='MAIN read all181 newPythonlines plusRUNBOOK and unchanged54-line publictransform. Frozenfull48prefixes fit, no filters; actualnewpairHTTP/owner/metrics and dimensionfixtures pass.',
        seeds='Generation202609360000..11; sampling202609370000..23; T.5,384output,4workers',
        checkpoint_policy='Nooptimizer/scoreselection; rawcalls persisted; noeligibility calculation or hostgold intransform',
        caps_seconds=dict(science=600,owner=700,external=800),
        limitations='Freshsamefamily notnewdataset; historychanges affectnewinstances, notpairedsameinstancehistoryeffect; representationandwording jointlychange; 12contextsnot24IID',
        quota_note='CPUdesign/preparationacceptedbefore20percentwinddown; finishthisboundedcomparison then prioritizeanalysis/GitHub/handoff',
        predecessor_sha256=driver.sha(previous),command=command))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','800',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=SIDE/'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
