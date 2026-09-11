"""Parent-owned one training and R→T readout; no independent GPU admission or retry."""
import argparse
import functools
import os
import signal
import subprocess
import time
import traceback
from pathlib import Path

import study as s


def remaining(deadline, cap, now=None):
    value = deadline - (time.time() if now is None else now)
    if value <= 0:
        raise TimeoutError('one shared work deadline reached')
    return min(cap, value)


@functools.lru_cache(maxsize=1)
def dependencies():
    st = s.stack()
    path = s.PRIOR / 'launch.py'
    with s.aliases({'study': st.prior, 'native': st.native}):
        original = s.load('rowmean_original_owned_lifecycle', path,
                          s.read(s.PRIOR / 'READY.json')['source_sha256'][str(path)])
    suite = original.dependencies()
    suite.life.install()
    # Immutable source authentication once; live PID/start/UID/PGID checks unchanged.
    suite.life.verify_amendment = functools.lru_cache(maxsize=1)(suite.life.verify_amendment)
    return suite


def execute(output):
    started = time.time()
    ready = s.verify()
    if output != s.ROOT / 'outputs/attempt-001':
        raise ValueError('only the exact new attempt namespace is prepared')
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu:
        raise ValueError('MAIN must assign the sole free GPU under its shared lock')
    output.mkdir(parents=True, exist_ok=False)
    deadline, work = started + 3300, started + 3180
    s.write(output / 'RUN.json', {'identity': ready['identity'], 'ready_sha256': s.sha(s.ROOT / 'READY.json'),
        'started_epoch': started, 'deadline_epoch': deadline, 'work_deadline_epoch': work,
        'gpu': gpu, 'phase_order': list(s.PHASES)})
    def expired(_sig, _frame):
        raise TimeoutError('3300s inclusive envelope or parent termination')
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
        signal.signal(sig, expired)
    signal.setitimer(signal.ITIMER_REAL, remaining(deadline, 3300))
    suite, stages, error = dependencies(), [], None
    try:
        argv = [str(s.TRAIN), str(s.ROOT / 'train.py'), 'run', '--output', str(output / 'training')]
        cap = remaining(work, 900)
        s.write(output / 'TRAIN_COMMAND.json', {'argv': argv, 'cap_seconds': cap, 'started_epoch': time.time()})
        with (output / 'training.log').open('x') as log:
            process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            observation = suite.life.observe(process.pid)
            if observation is None:
                raise RuntimeError('owned training process identity unavailable')
            owner = suite.life.safe_observation(observation)
            s.write(output / 'TRAIN_PROCESS.json', owner)
            try:
                if process.wait(timeout=cap):
                    raise RuntimeError('training returned nonzero; checkpoint/log retained')
            finally:
                suite.stop_child(process, owner)
                s.write(output / 'TRAIN_EXIT.json', {'returncode': process.returncode, 'ended_epoch': time.time()})
        row_selected = s.checkpoint(output / 'training', ready['identity'])
        token_selected = s.checkpoint(s.CONTROL, s.PRIOR_IDENTITY, s.CONTROL_SHA)
        for arm in s.PHASES:
            training, selected = (output / 'training', row_selected) if arm == 'equal_row' else (s.CONTROL, token_selected)
            stage = output / arm
            stage.mkdir()
            try:
                suite.start_service(stage, s.binding(arm, training, selected), time.time() + remaining(work, 180))
                argv = [str(s.NATIVE), str(s.ROOT / 'readout.py'), '--weight', arm, '--training', str(training),
                        '--binding', str(stage / 'BINDING.json'), '--endpoint', str(stage / 'service/endpoint-original.json'),
                        '--output', str(stage / 'rollout'), '--deadline', str(time.time() + remaining(work, 900))]
                suite.command(stage, 'collect', argv, 930, work)
                stages.append({'arm': arm, 'terminal': s.read(stage / 'rollout/TERMINAL.json')})
            finally:
                suite.release_service(stage)
    except BaseException as caught:
        error = {'type': type(caught).__name__, 'message': str(caught), 'traceback': traceback.format_exc()}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    terminal = {'complete': error is None, 'error': error, 'stages': stages,
                'elapsed_seconds': time.time() - started, 'deadline_epoch': deadline,
                'independent_analysis_deferred_until_after_release': True}
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
