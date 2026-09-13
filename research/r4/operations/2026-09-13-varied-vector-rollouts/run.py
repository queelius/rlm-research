"""MAIN admission: fresh G4 reward-contrast collection, no optimizer."""
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-13-state-representation/run.py'
spec = importlib.util.spec_from_file_location('varied_prior_operator', SOURCE)
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
driver = previous.driver
driver.ROOT = ROOT
SIDE = driver.SIDES / 'b05-varied-vector-rollouts-v1'
EXPECTED = 'a20b568cd8ee3d49cbd65b3e5aab41003c31921be91f7ed5669be5df69733c8d'

def execute():
    prior = driver.SIDES / 'b05-singleton-decomposition-v1/outputs/attempt-001/OWNER_TERMINAL.json'
    assert driver.read(prior)['released']
    driver.empty_gpu()
    assert driver.sha(SIDE / 'CPU_READY.json') == EXPECTED
    assert not (SIDE / 'outputs/attempt-001').exists()
    command = ['/project/alex_phd/envs/prime-rl-5990b1b/bin/python', str(SIDE / 'owner.py'), 'run', '--outer-seconds', '700']
    driver.write_once('ADMISSION.json', dict(epoch=time.time(), authority='MAIN', external_flock=True,
        ready_sha256=EXPECTED, command=command, planned_calls=64,
        question='Do varied G4 vectors supply useful native decision-level reward contrasts?',
        review='MAIN read all272 new Python lines, runbook, and actual HTTP/span fixtures.',
        seeds='train gen202609440000..15 sampling202609450000..63; held frozen separately',
        metrics='All64 sample outcomes,16 G4 groups, invalids, native span qualification and reward variation',
        checkpoint_policy='Every native call saved; no optimizer; held not executed; no output repair',
        caps_seconds=dict(science=600, owner=700, external=800),
        limitations='Diagnostic only; local versus joint training requires separate admission'))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=driver.GPU, OMP_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY'] = driver.read(driver.SIDES / 'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT / 'owner.log').open('x') as log:
        result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', '800', *command], cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    terminal = SIDE / 'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu()
    driver.write_once('QUEUE_TERMINAL.json', dict(epoch=time.time(), returncode=result.returncode, owner_terminal_sha256=driver.sha(terminal)))

if __name__ == '__main__':
    execute()
