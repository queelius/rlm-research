"""MAIN queues the fixed ID interface after the already-admitted dose readouts."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('ids_interface_lease_helpers',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'b05-eligible-ids-interface-v1'
EXPECTED='3fe8fff0d3d177f54171a54544998a2de8568b01743896254b1347afa97b9aa3'
PREVIOUS=ROOT.parent/'2026-09-12-fresh8-dose10-readout-queue/QUEUE_TERMINAL.json'

def execute():
    path=SIDE/'READY_RUN.json';assert driver.sha(path)==EXPECTED
    ready=driver.read(path);driver.verify_closure(ready)
    assert ready['planned_calls']==24 and ready['root_model_calls']==0
    driver.write_once('QUEUED.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,
        predecessor=str(PREVIOUS),wait_cap_seconds=2700,owner_cap_seconds=700,
        external_flock=True,review='MAIN read all464 source/test/preparation lines and RUNBOOK. Actual native6call/invalid-ID/no-eligibility-filter tests passed; exact qualified V3 child inputs pinned.',
        question='Does selecting only IDs recover more eligible choices than full-record reports, with identical inputs/model/seeds and deterministic lookup in both arms?',
        units='24 draws on12 stages nested in4 exposed root units',
        metrics='Exact ID sets over24; conditional precision/recall labelled with invalid/unknown; diagnostic all24 projections; CPUglobalcorrectness over32 dependent tuples; actual cost',
        seed_policy='Originalchildseeds/T.5/384maximum,4workers,zero parentmodelcalls',
        no_gold_repair=True,host_arithmetic_is_not_learned_model_skill=True,
        checkpoint_policy='Fixed base model; every native response; no optimizer/retry/outcome replacement'))
    deadline=time.monotonic()+2700
    while not PREVIOUS.exists():
        if time.monotonic()>=deadline:raise TimeoutError('preceding approved queue not terminal; no GPU launch')
        time.sleep(5)
    previous=driver.read(PREVIOUS)
    assert [row['phase'] for row in previous['phases']]==['train','held']
    driver.verify_closure(ready);driver.empty_gpu()
    output=SIDE/'outputs/attempt-001';assert not output.exists()
    command=ready['argv'];assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(SIDE/'owner.py'),'run','--outer-seconds','700']
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    driver.write_once('START.json',dict(epoch=time.time(),command=command,external_seconds=800,predecessor_sha256=driver.sha(PREVIOUS)))
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','800',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=output/'OWNER_TERMINAL.json';assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
