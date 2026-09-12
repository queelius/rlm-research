"""MAIN-reviewed bounded evidence representation comparison; external flock required."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec = importlib.util.spec_from_file_location('evidence_queue_helpers', SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / 'musique-evidence-preservation-v1'
READY = SIDE / 'CPU_READY.json'
EXPECTED = 'd9e00faec0d54e12311e27f1952066c5677c52df309c546723dcf015ca5307f1'

def execute():
    assert driver.sha(READY) == EXPECTED
    ready = driver.read(READY)
    driver.verify_closure(ready)
    assert ready['physical_calls'] == 72 and ready['final_slots'] == 24
    assert not Path(ready['output']).exists()
    driver.empty_gpu()
    driver.write_once('ADMISSION.json', {
        'authority': 'MAIN', 'epoch': time.time(), 'ready_sha256': EXPECTED,
        'ready_identity': ready['identity'], 'wrapper_sha256': driver.sha(__file__),
        'review': 'MAIN fully read all431 source/test/prepare lines and RUNBOOK. Actual owner verify passed1666 pins. Three focused CPU tests exercise actual six-call graph with only native HTTP response doubled. Reuses qualified V3 service and lifecycle.',
        'question': 'For identical selected source paragraphs, does returning original evidence outperform returning generated summaries?',
        'units': '12 previously exposed contexts,24 paired finals,72 physical calls',
        'cost_boundary': 'Natural3 versus5 calls per question; not input-token or natural-call-cost matched.',
        'checkpoint_policy': 'Save every physical request, response and outcome; preserve missingness and invalid selectors; no gold-dependent fallback.',
        'seed_rule': ready['role_seeds'], 'optimizer_steps': 0,
    })
    env = {**os.environ, 'CUDA_VISIBLE_DEVICES': driver.GPU, 'OMP_NUM_THREADS': '4',
           'PYTHONDONTWRITEBYTECODE': '1'}
    private = driver.read(driver.SIDES / 'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')
    env['STRICT_RLM_CALIBRATION_API_KEY'] = private['vllm']['api_key'][0]
    start = time.time()
    driver.write_once('START.json', {'epoch': start, 'command': ready['command'], 'external_seconds': 1050})
    with (ROOT / 'owner.log').open('x') as log:
        result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', '1050', *ready['command']],
                                cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    driver.write_once('EXIT.json', {'epoch': time.time(), 'returncode': result.returncode,
                                   'elapsed_seconds': time.time()-start})
    terminal = Path(ready['output']) / 'OWNER_TERMINAL.json'
    # Some inherited owners call the final receipt RESULT.json; require the
    # actual terminal release receipt, not a scientific success assumption.
    if not terminal.exists():
        terminal = Path(ready['output']) / 'RESULT.json'
    if not terminal.exists() or not driver.read(terminal).get('released'):
        raise RuntimeError('Owner release not authenticated; no subsequent launch')
    driver.empty_gpu()
    driver.write_once('QUEUE_TERMINAL.json', {'epoch': time.time(), 'returncode': result.returncode,
                                            'owner_terminal_sha256': driver.sha(terminal)})

if __name__ == '__main__':
    execute()
