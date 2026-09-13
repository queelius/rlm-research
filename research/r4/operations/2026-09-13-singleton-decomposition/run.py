"""MAIN bounded admission for fixed singleton decomposition."""
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-13-state-representation/run.py'
spec = importlib.util.spec_from_file_location('singleton_prior_operator', SOURCE)
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
driver = previous.driver
driver.ROOT = ROOT
SIDE = driver.SIDES / 'b05-singleton-decomposition-v1'
EXPECTED = '06d962c024298d58cb87abefb54f03d2019fdbe5fd298cfd47c38edcbda2094c'

def execute():
    assert (ROOT.parent / '2026-09-13-state-representation/QUEUE_TERMINAL.json').exists()
    driver.empty_gpu()
    assert driver.sha(SIDE / 'CPU_READY.json') == EXPECTED
    assert not (SIDE / 'outputs/attempt-001').exists()
    command = ['/project/alex_phd/envs/prime-rl-5990b1b/bin/python', str(SIDE / 'owner.py'), 'run', '--outer-seconds', '1000']
    driver.write_once('ADMISSION.json', dict(epoch=time.time(), authority='MAIN', external_flock=True,
        ready_sha256=EXPECTED, command=command, planned_calls=176,
        question='Does fixed one-candidate decomposition improve complete eligible sets?',
        review='MAIN read all new source, focused HTTP and union fixtures, and runbook.',
        seeds='generation202609420000..5; roots202609430000..11; scalar root+1000+index',
        metrics='All12 perarm complete sets, validity and unknown separate, partial scalar coverage separate, actual costs',
        checkpoint_policy='Every native call saved; no training; no repair or label-based filtering',
        caps_seconds=dict(science=900, owner=1000, external=1100),
        limitations='Six independent contexts; fixed decomposition, not learned routing; repeated policy input not compute matched'))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=driver.GPU, OMP_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY'] = driver.read(driver.SIDES / 'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT / 'owner.log').open('x') as log:
        result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', '1100', *command], cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    terminal = SIDE / 'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu()
    driver.write_once('QUEUE_TERMINAL.json', dict(epoch=time.time(), returncode=result.returncode, owner_terminal_sha256=driver.sha(terminal)))

if __name__ == '__main__':
    execute()
