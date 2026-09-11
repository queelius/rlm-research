"""Parent-invoked serial service→native generation→root update, fixed final8."""
import argparse
import ast
import functools
import os
import signal
import subprocess
import time
import traceback
import uuid
from pathlib import Path

import collect
import native as n
import study as s
from common import c, starting_decision
from export import export_attempt, authenticate_export


def schedule(step):
    if type(step) is not int or not 0 <= step <= 8:
        raise ValueError('campaign generation outside0..8')
    result = [f'validation-{step}'] if step in (0, 4, 8) else []
    if step in (0, 8):
        result.append(f'transfer-{step}')
    if step < 8:
        result.append(f'round-{step + 1}')
    return result


def time_budget(deadline, cap, now=None):
    remaining = deadline - (time.time() if now is None else now)
    if remaining <= 0:
        raise TimeoutError('one shared campaign work deadline reached')
    return min(cap, remaining)


@functools.lru_cache(maxsize=1)
def dependencies():
    st = n.stack()
    path = s.PRIOR / 'launch.py'
    pin = s.read(s.PRIOR / 'READY.json')['source_sha256'][str(path)]
    with s.aliases({'study': st.prior, 'native': st.native}):
        launcher = s.load('adaptive_rlvr_qualified_lifecycle_loader', path, pin)
    suite = launcher.dependencies()  # Includes exact /proc-absence amendment.
    suite.life.install()
    # Frozen source closure authentication is cached once per coordinator, not per
    # descendant observation. Dynamic PID/start/binding ownership checks remain live.
    suite.life.verify_amendment = functools.lru_cache(maxsize=1)(suite.life.verify_amendment)
    source = s.CAMPAIGN / 'campaign.py'
    s.check(source, s.read(s.PRIOR / 'READY.json')['source_sha256'][str(source)])
    node = next(v for v in ast.parse(source.read_text()).body if isinstance(v, ast.FunctionDef) and v.name == 'committed_policies')
    namespace = {'c': c, 'Path': Path}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source) + ':adaptive-checkpoint-namespace', 'exec'), namespace)
    return suite, namespace['committed_policies']


def stage_path(run, phase):
    kind, number = phase.split('-')
    return run / (f'round-{int(number):02d}/collection' if kind == 'round' else f'{kind}-{int(number):02d}')


def stage(run, phase, service, deadline, generation):
    directory = stage_path(run, phase)
    if (directory / 'export/MANIFEST.json').exists():
        authenticate_export(directory / 'export')
        return s.read(directory / 'export/MANIFEST.json')
    if directory.exists():
        status = s.read(directory / 'rollout/STATUS.json')
        if status['recorded'] != status['planned'] or status['stop_reason'] is not None:
            raise ValueError('partial/capped collection cannot be rerolled')
    else:
        directory.mkdir(parents=True)
        cap = time_budget(deadline, 1200 if phase.startswith('round-') else 900)
        spec_path = directory / 'CAPTURE_SPEC.json'
        collect.prepare_spec(phase, service / 'BINDING.json', service / 'service/endpoint-original.json', spec_path, cap, generation)
        argv = [str(s.NATIVE), str(s.ROOT / 'collect.py'), '--spec', str(spec_path),
                '--output', str(directory / 'rollout'), '--deadline', str(min(deadline, time.time() + cap))]
        dependencies()[0].command(service, 'collect-' + phase, argv, cap + 15, deadline)
    result = export_attempt(directory / 'rollout', directory / 'export')
    if result['integrity_failures']:
        raise ValueError('native role/mask/physical identity failure')
    if generation is not None and not result['training_group_episodes']:
        raise ValueError('no fresh within-prompt mixed reward group; no rerolls')
    return result


def train_round(run, step, deadline):
    suite, _ = dependencies()
    directory = run / f'round-{step:02d}'
    argv = [str(s.TRAIN), str(s.ROOT / 'train.py'), '--group', str(directory / 'collection/export/GROUP.json'),
            '--generation', str(directory / 'GENERATION.json'), '--output', str(directory / 'training'), '--deadline', str(deadline)]
    cap = time_budget(deadline, 750)
    s.write(directory / 'TRAIN_COMMAND.json', {'argv': argv, 'cap_seconds': cap, 'started_epoch': time.time()})
    with (directory / 'training.log').open('x') as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                   env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        observed = suite.life.observe(process.pid)
        if observed is None:
            raise RuntimeError('owned training subprocess exited before observation')
        owner = suite.life.safe_observation(observed)
        s.write(directory / 'TRAIN_OWNER.json', owner)
        try:
            code = process.wait(timeout=cap)
            if code:
                raise RuntimeError('owned trainer returned nonzero; retain checkpoint/log')
        finally:
            suite.stop_child(process, owner)
            s.write(directory / 'TRAIN_EXIT.json', {'returncode': process.returncode, 'ended_epoch': time.time()})


def execute(output, resume=False):
    started = time.time()
    manifest = s.verify_prepared()
    binding_path, _, _ = starting_decision()
    suite, committed = dependencies()
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu:
        raise ValueError('MAIN must supply the sole exclusively assigned GPU')
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
        s.write(output / 'RUN.json', {'campaign_id': manifest['campaign_id'], 'campaign_sha256': s.sha(s.ROOT / 'CAMPAIGN.json'),
                 'started_epoch': started, 'deadline_epoch': started + 7080, 'inclusive_deadline_epoch': started + 7200,
                 'gpu': gpu, 'starting_binding_path': str(binding_path), 'starting_binding_sha256': s.sha(binding_path)})
    envelope = s.read(output / 'RUN.json')
    if (envelope['campaign_sha256'] != s.sha(s.ROOT / 'CAMPAIGN.json') or envelope['gpu'] != gpu
            or envelope['starting_binding_sha256'] != s.sha(binding_path)):
        raise ValueError('resume campaign/start/device identity differs')
    if list(output.glob('STOP-*.json')):
        raise ValueError('terminal stop retained; no implicit continuation or retry')
    if (output / 'FINAL.json').exists():
        return s.read(output / 'FINAL.json')
    deadline = envelope['deadline_epoch']
    time_budget(envelope['inclusive_deadline_epoch'], 7200)
    def expired(_sig, _frame):
        raise TimeoutError('7200 inclusive campaign envelope or parent signal')
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
        signal.signal(sig, expired)
    signal.setitimer(signal.ITIMER_REAL, envelope['inclusive_deadline_epoch'] - time.time())
    try:
        for old in sorted((output / 'services').glob('*/SERVICE_REQUEST.json')):
            if not (old.parent / 'SERVICE_STOPPED.json').exists():
                suite.release_service(old.parent)
        policies = committed(output)
        while True:
            step = max(policies)
            phases = schedule(step)
            generation = None
            if step < 8:
                directory = output / f'round-{step + 1:02d}'
                generation = c.generation_identity(manifest['campaign_id'], step + 1, policies[step], s.digest(collect.planned(f'round-{step + 1}')))
                path = directory / 'GENERATION.json'
                if path.exists():
                    if s.read(path) != generation:
                        raise ValueError('stale round generation')
                else:
                    s.write(path, generation)
            pending = [phase for phase in phases if not (stage_path(output, phase) / 'export/MANIFEST.json').exists()]
            if pending:
                service = output / 'services' / f'step-{step:02d}-{uuid.uuid4().hex[:8]}'
                service.mkdir(parents=True)
                try:
                    suite.start_service(service, collect.binding_for(policies[step]), time.time() + time_budget(deadline, 180))
                    for phase in pending:
                        stage(output, phase, service, deadline, generation if phase.startswith('round-') else None)
                finally:
                    suite.release_service(service)
            if step == 8:
                break
            if not suite.life.v1.ports_free():
                raise ValueError('owned inference not released before optimizer')
            train_round(output, step + 1, deadline)
            policies = committed(output)
            if max(policies) != step + 1:
                raise ValueError('trainer exited without a committed fresh update')
        selection = {'rule': 'fixed final8; no validation selection', 'selected_step': 8, 'policy': policies[8]}
        s.write(output / 'SELECTION.json', selection)
        result = {'status': 'complete', 'optimizer_steps': 8, 'selection': selection,
                  'starting_policy': policies[0], 'planned_episodes': 184,
                  'stages': {phase: s.read(stage_path(output, phase) / 'export/MANIFEST.json')
                             for phase in ['validation-0', 'validation-4', 'validation-8', 'transfer-0', 'transfer-8']},
                  'elapsed_seconds': time.time() - envelope['started_epoch'], 'owned_service_released': True}
        s.write(output / 'FINAL.json', result)
        return result
    except BaseException as error:
        policies = committed(output)
        s.write(output / ('STOP-' + uuid.uuid4().hex + '.json'),
                {'status': 'stopped', 'type': type(error).__name__, 'reason': str(error),
                 'optimizer_steps': max(policies), 'last_policy': policies[max(policies)],
                 'elapsed_seconds': time.time() - envelope['started_epoch'], 'traceback': traceback.format_exc()})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run', 'resume'))
    parser.add_argument('--start-binding', type=Path)
    parser.add_argument('--output', type=Path, default=s.ROOT / 'outputs/attempt-001')
    args = parser.parse_args()
    if args.command == 'verify':
        print({'campaign_id': s.verify_prepared()['campaign_id'], 'gpu_calls': 0, 'start_binding_selected': False})
    else:
        if args.start_binding is None:
            raise ValueError('explicit MAIN start-binding argument required')
        os.environ['ADAPTIVE_RLVR_START_BINDING'] = str(args.start_binding.resolve())
        os.environ['ADAPTIVE_RLVR_START_SHA256'] = s.sha(args.start_binding)
        print(execute(args.output.resolve(), args.command == 'resume'))
