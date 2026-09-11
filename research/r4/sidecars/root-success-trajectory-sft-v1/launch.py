"""MAIN-owned serial training plus three phases, one clock and qualified release."""
import argparse
import functools
import os
import signal
import subprocess
import time
import traceback
from pathlib import Path
import study as s
import binding as b


def remaining(deadline, cap, now=None):
    value = deadline - (time.time() if now is None else now)
    if value <= 0:
        raise TimeoutError('shared work budget exhausted')
    return min(cap, value)


@functools.lru_cache(maxsize=1)
def dependencies():
    with s.aliases({'study': s.row}):
        module = s.load('success_qualified_owned_lifecycle', s.ROW / 'launch.py', '62d7d0049b5e3303f6e68247038290c7cde0d74e3394b4856fea0e3e138d6b46')
    return module.dependencies()


def execute(output):
    started = time.time()
    ready = s.verify()
    if output != s.ROOT / 'outputs/attempt-001':
        raise ValueError('only the exact new attempt is prepared')
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu:
        raise ValueError('MAIN assigns one empty GPU under the shared lock')
    output.mkdir(parents=True, exist_ok=False)
    deadline, work = started + 4500, started + 4380
    s.write(output / 'RUN.json', dict(identity=ready['identity'], ready_sha256=s.sha(s.ROOT / 'READY.json'),
        started_epoch=started, deadline_epoch=deadline, work_deadline_epoch=work, gpu=gpu, phase_order=s.phase_order()))
    def expired(_sig, _frame):
        raise TimeoutError('4500s inclusive envelope or parent termination')
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
        signal.signal(sig, expired)
    signal.setitimer(signal.ITIMER_REAL, remaining(deadline, 4500))
    stages, error = [], None
    try:
        suite = dependencies()
        argv = [str(s.TRAIN), str(s.ROOT / 'train.py'), 'run', '--output', str(output / 'training')]
        cap = remaining(work, 1200)
        s.write(output / 'TRAIN_COMMAND.json', dict(argv=argv, cap_seconds=cap, started_epoch=time.time()))
        with (output / 'training.log').open('x') as log:
            process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            observation = suite.life.observe(process.pid)
            if observation is None:
                raise RuntimeError('owned training identity unavailable')
            owner = suite.life.safe_observation(observation)
            s.write(output / 'TRAIN_PROCESS.json', owner)
            try:
                if process.wait(timeout=cap):
                    raise RuntimeError('training returned nonzero; checkpoint/log preserved')
            finally:
                suite.stop_child(process, owner)
                s.write(output / 'TRAIN_EXIT.json', dict(returncode=process.returncode, ended_epoch=time.time()))
        selected = {arm: b.selected(arm) for arm in s.phase_order()}
        for arm in s.phase_order():
            stage = output / arm
            stage.mkdir()
            try:
                suite.start_service(stage, b.binding(arm, selected[arm]), time.time() + remaining(work, 180))
                argv = [str(s.NATIVE), str(s.ROOT / 'readout.py'), '--weight', arm,
                        '--training', str(b.training_source(arm)), '--binding', str(stage / 'BINDING.json'),
                        '--endpoint', str(stage / 'service/endpoint-original.json'), '--output', str(stage / 'rollout'),
                        '--deadline', str(time.time() + remaining(work, 900))]
                suite.command(stage, 'collect', argv, 930, work)
                stages.append(dict(arm=arm, terminal=s.read(stage / 'rollout/TERMINAL.json')))
            finally:
                suite.release_service(stage)
    except BaseException as caught:
        error = dict(type=type(caught).__name__, message=str(caught), traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    terminal = dict(complete=error is None, error=error, stages=stages, elapsed_seconds=time.time() - started,
                    deadline_epoch=deadline, independent_analysis_deferred_until_after_release=True)
    s.write(output / 'TERMINAL.json', terminal)
    return terminal


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run'))
    parser.add_argument('--output', type=Path, default=s.ROOT / 'outputs/attempt-001')
    args = parser.parse_args()
    if args.command == 'verify':
        print({'identity': s.verify()['identity'], 'gpu_calls': 0})
    else:
        result = execute(args.output.resolve())
        print(result)
        raise SystemExit(0 if result['complete'] else 1)
