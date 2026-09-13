"""MAIN paired one-update training admission, under the shared GPU flock."""
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
source = ROOT.parent / '2026-09-13-state-representation/run.py'
spec = importlib.util.spec_from_file_location('paired_credit_operator', source)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
driver = prior.driver
driver.ROOT = ROOT
ARMS = [('local', '62f961601f164aec417bf636a2472f4caab17cde30c220451dfa7ad6581fcf64'),
        ('joint', 'a4ffa9de290941839ee75b19f2c0ae98fb69e845ad6a78ed79830b841562bfa1')]

def execute():
    driver.empty_gpu()
    evidence = []
    for arm, expected in ARMS:
        side = driver.SIDES / f'b05-vector-credit-{arm}-v2'
        assert driver.sha(side / 'READY.json') == expected
        ready = driver.read(side / 'READY.json')
        proof = driver.read(side / 'ENTRY_PROOF.json')
        assert proof['returncode'] == 0 and proof['ready_sha256'] == expected
        assert proof['subprocess_cuda_visible_devices'] == '' and proof['output_absent']
        assert ready['optimizer_steps'] == 1 and ready['denominator'] == 64
        assert ready['learning_rate'] == 1e-4 and ready['temperature'] == .5
        assert not Path(ready['output']).exists()
        evidence.append(dict(arm=arm, ready_sha256=expected, input_sha256=ready['shared_input_sha256'], command=ready['argv']))
    assert evidence[0]['input_sha256'] == evidence[1]['input_sha256']
    driver.write_once('ADMISSION.json', dict(epoch=time.time(), authority='MAIN', external_flock=True,
        question='Does decision-local credit outperform whole-response credit on the same sampled actions?',
        arms=evidence, review='MAIN reviewed math, trainer, scorer interfaces, CPU device repair and actual tiny scorer tests.',
        controls='Same64 actions, native decision-token mask, seeded zero-B initialization, LR1e-4, Adam and /64 denominator',
        boundary='Whole token includes inseparable comma/space; no fractional weighting; biased token-TIS2',
        checkpoint_policy='One fixed step each; initial tensors, gradients, Adam, RNG and checkpoint manifests saved',
        caps_per_arm_seconds=dict(science=900, owner=1000, external=1100),
        no_accuracy_claim_before_held_readout=True))
    outcomes = []
    for item in evidence:
        side = driver.SIDES / f"b05-vector-credit-{item['arm']}-v2"
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=driver.GPU, OMP_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
        env['LD_LIBRARY_PATH'] = '/export/software/system/nvidia/580.126.20/lib' + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
        with (ROOT / (item['arm'] + '.log')).open('x') as log:
            run = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', '1100', *item['command']], cwd=side, env=env, stdout=log, stderr=subprocess.STDOUT)
        terminal = side / 'outputs/attempt-001/OWNER_TERMINAL.json'
        assert terminal.exists() and driver.read(terminal)['owned_process_reaped']
        driver.empty_gpu()
        outcomes.append(dict(arm=item['arm'], returncode=run.returncode, terminal_sha256=driver.sha(terminal)))
        driver.write_once(item['arm'] + '-TERMINAL.json', outcomes[-1])
        if run.returncode != 0:
            break
    driver.write_once('QUEUE_TERMINAL.json', dict(epoch=time.time(), outcomes=outcomes))

if __name__ == '__main__':
    execute()
