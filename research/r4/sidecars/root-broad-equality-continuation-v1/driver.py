"""One explicit saved-round1 broad16 continuation; no collection/validation replay."""
import argparse
import fcntl
import json
import os
import signal
import time
from pathlib import Path

import common as a
import native

c, coordinator = a.c, a.coordinator
BASE_COMMAND = coordinator.impl.owned_command


def schedule():
    stages = [['training', 1]]
    for step in range(2, 17):
        stages.extend([['collection', step], ['training', step]])
        if step % 4 == 0:
            stages.append(['validation', step])
    return stages + [['fixed_final_selection', 16], ['transfer', 'original'], ['transfer', 'final']]


def run_envelope(started, gpu):
    return {'campaign_id': c.read(a.BROAD / 'CAMPAIGN.json')['campaign_id'],
        'campaign_sha256': c.file_hash(a.BROAD / 'CAMPAIGN.json'),
        'started_epoch': started, 'deadline_epoch': started + a.WORK_SECONDS, 'gpu': gpu,
        'inherited_optimizer_steps': 0, 'prior_elapsed_seconds': a.PRIOR_SECONDS,
        'new_work_cap_seconds': a.WORK_SECONDS, 'inclusive_cap_seconds': a.INCLUSIVE_SECONDS,
        'original_total_work_seconds': 18000, 'namespace': a.ROOT.name,
        'old_stop_preserved': True, 'rerolled_episodes': 0, 'replayed_validation_episodes': 0}


def dispatch_command(command):
    if command[:2] == [str(c.TRAIN_PYTHON), str(a.BROAD / 'campaign_train.py')]:
        return [command[0], str(a.ROOT / 'train.py'), *command[2:]]
    if command[:3] == [str(c.NATIVE_PYTHON), str(a.BROAD / 'campaign_native.py'), 'collect']:
        return [command[0], str(a.ROOT / 'native.py'), *command[2:]]
    raise ValueError('unexpected subprocess route; no new workflow authorized')


def owned_command(command, log_path, timeout, *, gpu=False):
    dispatched = dispatch_command(command)
    c.write_once(Path(log_path).with_suffix('.dispatch.json'), {'original_command': command,
        'actual_command': dispatched, 'gpu': gpu, 'timeout': timeout,
        'amendment_sha256': c.file_hash(a.ROOT / 'AMENDMENT.json')})
    return BASE_COMMAND(dispatched, log_path, timeout, gpu=gpu)


def stage_inherited(output):
    output = Path(output)
    refs = [(a.PRIOR_RUN / 'validation-00', output / 'validation-00'),
            (a.ROOT / 'prepared-round01', output / 'round-01/collection/export')]
    mapping = []
    for source, destination in refs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(source, target_is_directory=True)
        mapping.append({'source': str(source), 'destination': str(destination), 'reference_only': True,
            'manifest_sha256': c.file_hash(source / ('export/MANIFEST.json' if source.name == 'validation-00' else 'MANIFEST.json'))})
    generation = c.read(a.PRIOR_RUN / 'round-01/GENERATION.json')
    c.write_once(output / 'round-01/GENERATION.json', generation)
    c.write_once(output / 'INHERITED_STAGES.json', {'references': mapping,
        'old_stop_path': str(a.STOP), 'old_stop_sha256': a.STOP_SHA,
        'generation_sha256': c.file_hash(output / 'round-01/GENERATION.json'),
        'round1_rollout_source': str(a.PRIOR_RUN / 'round-01/collection/rollout'),
        'rerolled_episodes': 0, 'reapplied_updates': 0})


def verify_ready():
    amendment = a.verify_amendment()
    ready = c.read(a.ROOT / 'READY.json')
    if ready['amendment_sha256'] != c.file_hash(a.ROOT / 'AMENDMENT.json'):
        raise ValueError('READY amendment differs')
    c.authenticate(ready['source_sha256'])
    c.authenticate(ready['artifact_sha256'])
    return {'amendment_id': amendment['amendment_id'], 'prior_steps': 0,
        'prepared_group_episodes': len(c.read(a.ROOT / 'prepared-round01/GROUP.json')['episodes']),
        'schedule': schedule(), 'gpu_calls': 0}


def main():
    started = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['verify', 'run'])
    parser.add_argument('--output', type=Path, default=a.ROOT / 'outputs/attempt-001')
    args = parser.parse_args()
    checked = verify_ready()
    if args.command == 'verify':
        print(json.dumps(checked, sort_keys=True), flush=True)
        return
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('parent must assign one exclusive GPU and service key')
    output = args.output.resolve()
    if output.parent != a.ROOT / 'outputs' or output.exists():
        raise ValueError('new owned continuation output required; no implicit resume')
    def expired(sig, frame):
        raise TimeoutError('remaining broad16 inclusive cap or parent signal')
    for sig in (signal.SIGALRM, signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, expired)
    signal.setitimer(signal.ITIMER_REAL, max(.001, a.INCLUSIVE_SECONDS - (time.time() - started)))
    # Same campaign lease; CPU prepare/verify never opens or retains this lock.
    with (a.BROAD / 'COORDINATOR.lock').open('a') as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        output.mkdir(parents=True, exist_ok=False)
        c.write_once(output / 'RUN.json', {**run_envelope(started, gpu),
            'equality_amendment_id': checked['amendment_id'],
            'prior_stop_to_entry_gap_seconds': started - a.STOP.stat().st_mtime})
        stage_inherited(output)
        c.write_once(output / 'EXECUTION.json', {'ready_sha256': c.file_hash(a.ROOT / 'READY.json'),
            'amendment_sha256': c.file_hash(a.ROOT / 'AMENDMENT.json'), 'schedule': schedule(),
            'old_stop_preserved': True, 'observer_fix': 'inherited exact broad16 disappearing-process absence patch'})
        native.install()
        coordinator.impl.owned_command = owned_command
        try:
            result = coordinator.impl.run_campaign(argparse.Namespace(output=output, resume=True))
            print(json.dumps(result, sort_keys=True), flush=True)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    main()
