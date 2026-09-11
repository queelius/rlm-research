"""Training-only GPU dispatch correction; evaluation still uses the CPU client."""
import argparse
import os
from pathlib import Path
import subprocess
import time
import postcapture_owner as p

OUTPUT = p.s.SOURCE_ROOT / 'outputs/attempt-003'


class TrainingSuite:
    def __init__(self, base):
        self.base = base

    def __getattr__(self, name):
        return getattr(self.base, name)

    def command(self, stage, label, argv, cap, deadline):
        if label != 'six-updates':
            if label in ('dev8', 'protected72'):
                argv = list(argv)
                if argv[1] != str(p.s.SOURCE_ROOT / 'postcapture_readout.py'):
                    raise ValueError('unexpected native readout entry point')
                argv[1] = str(p.s.SOURCE_ROOT / 'postcapture_readout_gpu.py')
            return self.base.command(stage, label, argv, cap, deadline)
        gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
        if not gpu or ',' in gpu:
            raise ValueError('one assigned GPU required by training subprocess')
        p.s.write(stage / (label + '-COMMAND.json'), dict(argv=argv, started_epoch=time.time(),
            cap_seconds=min(cap, deadline-time.time()), gpu_visible_to_command=True,
            assigned_cuda_visible_devices=gpu))
        with (stage / (label + '.log')).open('x') as log:
            process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            observed = self.base.life.observe(process.pid)
            if observed is None:
                process.wait(timeout=5)
                raise RuntimeError('training exited before process ownership observation')
            if observed['pgid'] != process.pid or observed['uid'] != os.getuid():
                raise ValueError('training process identity mismatch')
            owner = self.base.life.safe_observation(observed)
            p.s.write(stage / (label + '-PROCESS.json'), owner)
            try:
                if process.wait(timeout=max(.001, min(cap, deadline-time.time()))) != 0:
                    raise RuntimeError('training failed; preserve log and checkpoints')
            finally:
                self.base.stop_child(process, owner)
                p.s.write(stage / (label + '-EXIT.json'), dict(
                    returncode=process.returncode, ended_epoch=time.time()))


def admission():
    value = p.admit_complete_capture()
    old = p.s.SOURCE_ROOT / 'outputs/attempt-002'
    failure = p.s.read(old / 'training/FAILURE.json')
    terminal = p.s.read(old / 'OWNER_TERMINAL.json')
    if failure['message'] != 'MAIN must assign exactly one GPU' or not terminal['released']:
        raise ValueError('exact pre-model GPU environment failure required')
    if (old / 'training/LOAD_AUDIT.json').exists() or list((old / 'training').glob('checkpoint-*')):
        raise ValueError('no prior model loading or updates may be replaced')
    receipt = p.s.read(p.OPERATIONS / '2026-09-10-after-capture-training-only' /
                      'attempt-001/question_sensitive_training_only/EXIT.json')
    if receipt['gpu_pids_after_exit']:
        raise ValueError('previous training-only owner did not release GPU')
    if sum(value['original_and_recovery_outer_seconds']) + receipt['elapsed_seconds'] + 4800 > 10800:
        raise ValueError('combined10800 active ceiling')
    return {**value, 'prior_gpu_visibility_failure_seconds': receipt['elapsed_seconds']}


def verify():
    p.verify()
    ready = p.s.read(p.s.SOURCE_ROOT / 'POSTCAPTURE_GPU_READY.json')
    if p.s.digest({k: v for k, v in ready.items() if k != 'identity'}) != ready['identity']:
        raise ValueError('GPU-dispatch amendment identity')
    for path, pin in ready['files_sha256'].items():
        if p.s.sha(path) != pin:
            raise ValueError('GPU-dispatch amendment source changed')
    return admission()


def execute(output):
    verify()
    previous_dependencies = p.dependencies
    previous_admission = p.admit_complete_capture
    p.POSTCAPTURE_OUTPUT = OUTPUT
    p.b.OUTPUT = OUTPUT
    p.dependencies = lambda: TrainingSuite(previous_dependencies())
    # Admission above adds the failed pre-model attempt to the combined budget.
    # The underlying owner retains the unchanged complete72 corpus admission.
    try:
        return p.execute(output)
    finally:
        p.dependencies = previous_dependencies
        p.admit_complete_capture = previous_admission


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run'))
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.command == 'verify':
        print(verify())
    else:
        # The readout subprocess is separately routed to the same output namespace.
        result = execute(args.output)
        print(dict(complete=result['complete'], released=result['released']))
        raise SystemExit(0 if result['complete'] else 1)
