"""MAIN admission for three frozen public representations, after vector release."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec = importlib.util.spec_from_file_location('state_representation_lease', SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / 'b05-state-representation-v1'
EXPECTED = 'e4d9bb044e40a71423bf3a2bb27a09a1cccc9405b8aed7bee8ca446fc402165a'

def execute():
    previous = ROOT.parent / '2026-09-13-decision-vector/QUEUE_TERMINAL.json'
    assert previous.exists()
    driver.empty_gpu()
    assert driver.sha(SIDE / 'READY.json') == EXPECTED
    ready = driver.read(SIDE / 'READY.json')
    command = ready['argv']
    assert command == ['/project/alex_phd/envs/prime-rl-5990b1b/bin/python', str(SIDE / 'owner.py'), 'run', '--outer-seconds', '1000']
    assert ready['planned_physical_calls'] == 72 and ready['all_candidates_retained']
    extra = driver.read(SIDE / 'TRANSPORT_SCORING_ADDENDUM.json')
    assert extra['returncode'] == 0 and extra['ready_sha256'] == EXPECTED and extra['asserted_transport_valid'] == 3
    cross = driver.read(SIDE / 'CROSS_PANEL_AUDIT.json')
    assert cross['root_ids_disjoint'] and cross['candidate_ids_disjoint']
    assert not (SIDE / 'outputs/attempt-001').exists()
    driver.write_once('ADMISSION.json', dict(epoch=time.time(), authority='MAIN',
        external_flock=True, ready_sha256=EXPECTED, command=command,
        question='Does grouping unchanged public records help, or is resolved state needed?',
        review='MAIN read new source, original and additive native transport/scoring fixtures, prospective data/normalizer and runbook. No sealed source changed.',
        seeds='generation202609400000..11; decoding202609410000..23; T.5/384/4workers',
        metrics='All24 perarm exact sets; strict sorting and validity separate; valid-set BA/confusion with denominators and all costs',
        checkpoint_policy='No optimizer; native calls persisted; no label-based filtering or repairs',
        caps_seconds=dict(science=900, owner=1000, external=1100),
        additive_test_sha256=driver.sha(SIDE / 'TRANSPORT_SCORING_ADDENDUM.json'),
        cross_panel_sha256=driver.sha(SIDE / 'CROSS_PANEL_AUDIT.json'),
        limitations='Wording and token lengths differ; fresh same-family cases, not pure resolution or new-dataset transfer',
        quota='18% remaining; user proceed and on-disk override authorize research'))
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
