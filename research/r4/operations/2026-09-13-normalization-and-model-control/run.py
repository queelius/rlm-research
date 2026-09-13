"""MAIN-reviewed public preprocessing then fixed alternative-model feasibility."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec=importlib.util.spec_from_file_location('normalization_alternative_lease',SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver);driver.ROOT=ROOT
STAGES=[
    ('normalization','b05-public-normalization-held9-v1','CPU_READY.json',
     'c604f3e4de142862bf8ab62d5be6a948a9ff168bccb6e02c94837452f412584a','owner.py','attempt-001',700,800),
    ('alternative8b','b05-qwen3-8b-direct-oracle-v1','READY_LIFECYCLE_REPAIR.json',
     '8b2ab88a037e7fd4e84c3a077011884c3cd1bbcd2566de58078a0a844c31862b','owner_v3.py','attempt-003',450,550),
]

def execute():
    previous=ROOT.parent/'2026-09-13-selection-rl-readout/QUEUE_TERMINAL.json'
    assert previous.exists();driver.empty_gpu()
    driver.write_once('ADMISSION.json',dict(epoch=time.time(),authority='MAIN',external_flock=True,
        predecessor_sha256=driver.sha(previous),wrapper_sha256=driver.sha(__file__),
        normalization=dict(
            question='Does resolving public updates and latest checks before delegation improve eligibility selection?',
            comparison='Fresh raw and normalized released-base controls on sameheld9 stages×2 pairedseeds; allIDs retained, noeligibility calculation/hostgold intransform',
            metric='Unordered exact primary, BA/precision/recall with explicitvaliddenominators; sortedformatseparate and nativecost',
            review='MAIN read321 Pythonlines+RUNBOOK and inherited baseowner; twofixtures exercise applied/draft/removal/latest/missing/allID rules and actual pairedHTTP/native decode/owner namespace.',
            seeds='202609330000..17,T.5,384output,4workers; inputs and explanatorywording jointlychange',
            caps_seconds=dict(science=600,owner=700,external=800)),
        alternative8b=dict(
            question='Can cached post-trained8B solve same4direct/4perfect-report roots?',
            comparison='Same8 frozen B05V3 prompts/seeds/sourcegrader, checkpoint-own nonthinkingtemplate, nofresh4Bcontrols',
            review='MAIN read original250lines, clockrepair and actualHTTPtest, lifecycle_v3 and additiveowner/collector/test/seal. Actualstart→claim→release fixture passed. Failed002 preserved with ownedcleanup.',
            metric='True-source correctness/validity/consistency/cost; all8 available orunknownseparate',
            limitations='Alternativecheckpointcalibration, notpureparameter-sizeeffect; oracleexactchildreports nondeployable, no rootanswer',
            caps_seconds=dict(science=300,owner=450,external=550)),
        checkpoint_policy='Nooptimizer or checkpointselection; persist eachnativecall; independentsecondstage regardlessfirstscore afterconfirmedrelease; noimplicitretry'))
    phases=[]
    for name,side_name,receipt,expected,entry,attempt,owner_seconds,external in STAGES:
        side=driver.SIDES/side_name;path=side/receipt
        assert driver.sha(path)==expected
        ready=driver.read(path);driver.verify_closure(ready);driver.empty_gpu()
        assert not (side/'outputs'/attempt).exists()
        command=ready['argv']
        assert command==['/project/alex_phd/envs/prime-rl-5990b1b/bin/python',str(side/entry),'run','--outer-seconds',str(owner_seconds)]
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=driver.GPU,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
        env['STRICT_RLM_CALIBRATION_API_KEY']=driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
        driver.write_once(name+'-START.json',dict(epoch=time.time(),ready_sha256=expected,command=command,external_seconds=external))
        with (ROOT/(name+'.log')).open('x') as log:
            result=subprocess.run(['timeout','--signal=TERM','--kill-after=30',str(external),*command],cwd=side,env=env,stdout=log,stderr=subprocess.STDOUT)
        terminal=side/'outputs'/attempt/'OWNER_TERMINAL.json'
        assert terminal.exists() and driver.read(terminal).get('released')
        driver.empty_gpu();phases.append(dict(name=name,returncode=result.returncode,epoch=time.time(),owner_terminal_sha256=driver.sha(terminal)))
        driver.write_once(name+'-TERMINAL.json',phases[-1])
    driver.write_once('QUEUE_TERMINAL.json',dict(epoch=time.time(),phases=phases))

if __name__=='__main__':execute()
