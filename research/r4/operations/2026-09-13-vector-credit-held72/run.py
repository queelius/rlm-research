"""MAIN final bounded held-out readout before the ten-percent account reserve."""
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
source = ROOT.parent / '2026-09-13-state-representation/run.py'
spec = importlib.util.spec_from_file_location('held72_prior_operator', source)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
driver = prior.driver
driver.ROOT = ROOT
SIDE = driver.SIDES / 'b05-vector-credit-held72-eval-v3'
EXPECTED = '56d8bdbe78dfeebac1db039978117f0c79b07418081477440acadd9082b01bca'

def execute():
    driver.empty_gpu()
    assert driver.sha(SIDE / 'READY.json') == EXPECTED
    ready = driver.read(SIDE / 'READY.json')
    proof = driver.read(SIDE / 'CPU_TESTS.json')
    assert proof['returncode'] == 0 and proof['ready_sha256'] == EXPECTED
    assert ready['planned_calls'] == 72 and ready['no_training_context_calls']
    assert not (SIDE / 'outputs/attempt-001').exists()
    driver.write_once('ADMISSION.json', dict(epoch=time.time(), authority='MAIN', external_flock=True,
        ready_sha256=EXPECTED, command=ready['argv'], question='Does local or joint RL improve full selection on frozen held cases?',
        review='MAIN read owner/collector/study/metrics and repaired three-alias actual HTTP scoring fixture; checkpoint qualifiers passed.',
        seeds='Already frozen202609470000..23; same24 held requests perarm base/local/joint',
        checkpoint_policy='Native calls persisted; no further optimizer, no repair or checkpoint selection',
        caps_seconds=dict(science=600, owner=700, external=800),
        budget='User preserve10%; final targeted readout before consolidation'))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=driver.GPU, OMP_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY'] = driver.read(driver.SIDES / 'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT / 'owner.log').open('x') as log:
        result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', '800', *ready['argv']], cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    terminal = SIDE / 'outputs/attempt-001/OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal)['released']
    driver.empty_gpu()
    driver.write_once('QUEUE_TERMINAL.json', dict(epoch=time.time(), returncode=result.returncode, terminal_sha256=driver.sha(terminal)))

if __name__ == '__main__':
    execute()
