"""MAIN-reviewed independent selection update and fresh financial replication."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '2026-09-12-rl-perturbation-chain/run.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'a10a6b7c6960c8e4a717c40da642389ddea8da03dc81b88d6d304457c5e68347'
spec = importlib.util.spec_from_file_location('selection_finqa_lease', SOURCE)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.ROOT = ROOT
STAGES = [
    ('selection', 'b05-flat-selection-rl-v1', 'READY.json',
     '7a2fe51f53402604ad3c3f437fd61d96ff347423417859b99916e720c85d6aa5', 1200),
    ('finqa', 'finqa-two-example-fresh16-v1', 'CPU_READY.json',
     '6fb1607ad82554dcccdf761fdff781ae939d6feda414bbdcaf0c57b6d227107f', 800),
]


def execute():
    previous = ROOT.parent / '2026-09-12-fresh32-dose-transfer-repair/QUEUE_TERMINAL.json'
    assert [x['arm'] for x in driver.read(previous)['phases']] == ['cp32', 'lr1e4']
    driver.empty_gpu()
    driver.write_once('ADMISSION.json', dict(
        authority='MAIN', epoch=time.time(), wrapper_sha256=driver.sha(__file__),
        predecessor_sha256=driver.sha(previous), external_flock=True,
        question='Can feedback on actual item selection change the helper policy; independently, does the financial interface result repeat on new pages?',
        selection=dict(
            start='Released 4B base plus fresh zero-B LoRA, never cp32 weights',
            objective='Present-class balanced accuracy; G2 RLOO, denominator18, eight nonzero actions, ten zero actions, 1845 selected array tokens',
            seed=202609320001, learning_rate=1e-4, optimizer_steps=1,
            metric='Separate fixed base/cp1 train18 plus frozen fresh held18 readout required; no claim from gradient alone',
            checkpoint_policy='Initial adapter and RNG, replay and token logps, gradients, Adam and fixed checkpoint0001/STEP_COMMIT',
            review='MAIN read study/core/train/owner/data/test/prepare/checkpoint, plan and actual CPU-entry receipt. Two fixtures and real CUDA-hidden entry passed.',
            caps_seconds=dict(science=900, owner=1100, external=1200)),
        finqa=dict(
            comparison='Same two synthetic examples and fixed interpreter; next16 hash-ranked distinct official dev pages excluding prior16, no gold/annotation filter',
            seeds='202609300000+i paired within16; T.5,384 output,4 workers',
            metric='Provided-target equality, DSL validity, native cost and source-grounding; all32 available/unknown separate',
            checkpoint_policy='Fixed released base, every native reply saved; no optimizer, prompt search or target repair',
            review='MAIN read all198 Python lines and RUNBOOK; selection reconstructed and all32 frozen prefixes equal unchanged demonstration builder; actual first-pair HTTP fixture passed.',
            caps_seconds=dict(science=600, owner=700, external=800)),
        continuation='FinQA proceeds regardless selection-training score/status after confirmed process release; learned-checkpoint evaluation needs separate READY',
        limitations='Exploratory, same-family held selection stages and FinQA dev pages; not learned recursion or broad generalization'))
    phases = []
    for name, side_name, receipt, expected, cap in STAGES:
        side = driver.SIDES / side_name
        path = side / receipt
        assert driver.sha(path) == expected
        ready = driver.read(path)
        driver.verify_closure(ready)
        driver.empty_gpu()
        output = side / 'outputs/attempt-001'
        assert not output.exists()
        command = ready['argv']
        if name == 'selection':
            assert command == ['/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python', str(side/'owner.py'), 'run']
            assert ready['learning_rate'] == 1e-4 and ready['init_seed'] == 202609320001
            assert ready['denominator'] == 18 and ready['nonzero_actions'] == 8
        else:
            assert command == ['/project/alex_phd/envs/prime-rl-5990b1b/bin/python', str(side/'owner.py'), 'run', '--outer-seconds', '700']
            assert ready['planned_physical_calls'] == 32
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=driver.GPU, OMP_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
        env['LD_LIBRARY_PATH'] = '/export/software/system/nvidia/580.126.20/lib:' + env.get('LD_LIBRARY_PATH', '')
        if name == 'finqa':
            env['STRICT_RLM_CALIBRATION_API_KEY'] = driver.read(driver.SIDES/'leaf-output-cue-order-v1/owned/attempt-001/service/inference.json')['vllm']['api_key'][0]
        driver.write_once(name+'-START.json', dict(epoch=time.time(), command=command, ready_sha256=expected, external_seconds=cap))
        with (ROOT/(name+'.log')).open('x') as log:
            result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=30', str(cap), *command], cwd=side, env=env, stdout=log, stderr=subprocess.STDOUT)
        terminal = output/'OWNER_TERMINAL.json'
        assert terminal.exists()
        released = 'owned_process_reaped' if name == 'selection' else 'released'
        assert driver.read(terminal).get(released)
        driver.empty_gpu()
        phases.append(dict(name=name, returncode=result.returncode, owner_terminal_sha256=driver.sha(terminal), epoch=time.time()))
        driver.write_once(name+'-TERMINAL.json', phases[-1])
    driver.write_once('QUEUE_TERMINAL.json', dict(epoch=time.time(), phases=phases))


if __name__ == '__main__':
    execute()
