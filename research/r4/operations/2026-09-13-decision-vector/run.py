"""MAIN admission for the bounded normalized-list/boolean-vector comparison."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec = importlib.util.spec_from_file_location('decision_vector_lease', SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / 'b05-decision-vector-v1'
EXPECTED = '992d7159904040919776081d768adb6fe89f3f556cb2c05e4bef3402fa19999c'

def execute():
    driver.empty_gpu()
    assert driver.sha(SIDE / 'CPU_READY.json') == EXPECTED
    ready = driver.read(SIDE / 'CPU_READY.json')
    command = ready['argv']
    assert command == ['/project/alex_phd/envs/prime-rl-5990b1b/bin/python', str(SIDE / 'owner.py'), 'run', '--outer-seconds', '700']
    assert ready['planned_physical_calls'] == 48 and ready['normalized_records_and_policy_identical']
    assert not (SIDE / 'outputs/attempt-001').exists()
    # The reviewed owner checks its closure; do not duplicate its ancestry walk here.
    driver.write_once('ADMISSION.json', dict(epoch=time.time(), authority='MAIN',
        external_flock=True, ready_sha256=EXPECTED, command=command,
        question='Does one explicit decision per candidate improve complete selection on the same normalized public input?',
        review='MAIN read all new source, parser/native HTTP fixture, RUNBOOK and readiness; two focused tests pass.',
        seeds='generation202609380000..11; decoding202609390000..23; T.5/384/4workers',
        metrics='Exact sets over24 planned perarm; strict sorting separate; invalid-known and unknown distinct; matched-valid BA and all costs',
        checkpoint_policy='No optimizer; persist every native request/response; never repair invalid vectors',
        caps_seconds=dict(science=600, owner=700, external=800),
        quota='User proceed and on-disk September12 override authorize remaining19% research; old reserve thresholds historical'))
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
