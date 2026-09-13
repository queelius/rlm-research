"""One prospectively fixed larger selection update; no continuation or sweep."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('selection_dose10_lease',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
SIDE=driver.SIDES/'b05-flat-selection-rl-dose10-v1'
EXPECTED='f845658e39448ab0f7836f0da09f8a8e9a5518400450ede7d513c28b7ef6da2b'

def execute():
    previous=ROOT.parent/'2026-09-13-normalization-and-model-control/QUEUE_TERMINAL.json'
    assert previous.exists();driver.empty_gpu()
    path=SIDE/'READY.json';assert driver.sha(path)==EXPECTED
    ready=driver.read(path);driver.verify_closure(ready)
    assert ready['learning_rate']==1e-3 and ready['denominator']==18 and ready['optimizer_steps']==1
    assert ready['exact_initial_tensor_gate'] and not ready['continuation']
    assert not (SIDE/'outputs/attempt-001').exists()
    command=ready['argv']
    assert command==['/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python',str(SIDE/'owner.py'),'run']
    driver.write_once('ADMISSION.json',dict(epoch=time.time(),authority='MAIN',ready_sha256=EXPECTED,external_flock=True,
        question='Does a single larger update strengthen local selection learning, transfer, or cause overshoot?',
        context='LR1e-4 train BA+.04065 over17valid,5trueFPremovals with2eligibleadditions/2omissions; heldBA-.00511, noexactgain',
        comparison='Same originalzero-B tensors/seed/batch/mask/G2/all18/clip1/TIS2/freshAdam; LR1e-3 onlyrecipechange, notcontinuation',
        metric='Fixed freshbase/cp1 train18 and exposedheld18 readout required regardlessscore; no improvement inferred fromweights',
        review='MAIN read all161 newPythonlines plusRUNBOOK and originaltrainer; initialtensoridentity mandatory, actual freshAdamtest and unmocked CPUentry passed.',
        checkpoint_policy='Onefixedcp1, actualinitialidentity/gradients/probability/replay/Adam/RNG/STEP_COMMIT, no automatic secondoptimizer',
        caps_seconds=dict(science=900,owner=1100,external=1200),
        limitations='Exploratorydose/overshootprobe onexposedheld9stages, notisolated deterministicgradientrescaling or prooflowLRcausednull',
        predecessor_sha256=driver.sha(previous),command=command))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    env['LD_LIBRARY_PATH']='/export/software/system/nvidia/580.126.20/lib:'+env.get('LD_LIBRARY_PATH','')
    with (ROOT/'owner.log').open('x') as log:
        result=subprocess.run(['timeout','--signal=TERM','--kill-after=30','1200',*command],cwd=SIDE,env=env,stdout=log,stderr=subprocess.STDOUT)
    terminal=SIDE/'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('owned_process_reaped')
    driver.empty_gpu();driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),returncode=result.returncode,owner_terminal_sha256=driver.sha(terminal)))

if __name__=='__main__':execute()
