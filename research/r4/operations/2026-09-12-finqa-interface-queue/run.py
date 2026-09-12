"""MAIN admits the frozen paired FinQA comparison; external flock is required."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec = importlib.util.spec_from_file_location('finqa_lease_helpers', SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
SIDE = driver.SIDES / 'finqa-scalar-vs-dsl-v1'
EXPECTED = '6df8bd380dfc0837405304f0bfc34c55d04ea0dcdff3212a63fdf97d66e7d1e0'

def execute():
    ready_path = SIDE / 'CPU_READY.json'
    assert driver.sha(ready_path) == EXPECTED
    ready = driver.read(ready_path)
    driver.verify_closure(ready)
    assert ready['planned_physical_calls'] == 32 and ready['paired_context_units'] == 16
    previous = driver.SIDES / 'b05-eligible-ids-interface-v1/outputs/attempt-001/OWNER_TERMINAL.json'
    assert driver.read(previous)['released']
    driver.empty_gpu()
    output = SIDE / 'outputs/attempt-001'
    assert not output.exists()
    command = ready['argv']
    assert command == ['/project/alex_phd/envs/prime-rl-5990b1b/bin/python', str(SIDE / 'owner.py'), 'run', '--outer-seconds', '700']
    driver.write_once('START.json', dict(epoch=time.time(), authority='MAIN', ready_sha256=EXPECTED,
        question='Does model-written arithmetic with host execution help on financial-report questions versus direct numeric answers?',
        metric='Provided target equality, invalid and unavailable separate; paired wins/losses; all16 retained including annotation flags; actual token cost',
        review='MAIN read all new source, tests, preparation and frozen-prefix fixture; two focused tests and exact frozen pair passed.',
        caps=dict(science_seconds=600, owner_seconds=700, external_seconds=800),
        seed_policy='202609290000+i paired by context; T=.5;384 output tokens each;4 workers',
        checkpoint_policy='Each native request and response saved; fixed base4B, no training or retries',
        known_limitations='Small exploratory dev panel; adapted JSON DSL, not official program accuracy; supplied targets may be noisy; not learned recursive decomposition',
        predecessor_sha256=driver.sha(previous), external_flock=True, command=command))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=driver.GPU, OMP_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
    env['STRICT_RLM_CALIBRATION_API_KEY'] = driver.read(driver.SIDES / 'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
    with (ROOT / 'owner.log').open('x') as log:
        result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', '800', *command], cwd=SIDE, env=env, stdout=log, stderr=subprocess.STDOUT)
    terminal = output / 'OWNER_TERMINAL.json'
    assert terminal.exists() and driver.read(terminal).get('released')
    driver.empty_gpu()
    driver.write_once('QUEUE_TERMINAL.json', dict(epoch=time.time(), returncode=result.returncode, owner_terminal_sha256=driver.sha(terminal)))

if __name__ == '__main__':
    execute()
