"""Bounded training-only continuation; no acquisition or baseline rerun."""
import argparse
import os
from pathlib import Path
import signal
import sys
import time
import recovery_study_v3 as s
import recovery_owner_v4 as previous
import recovery_owner_v3 as usage
import postcapture_binding as b

POSTCAPTURE_OUTPUT = b.OUTPUT
PREVIOUS_OUTPUT = s.ATTEMPT
OPERATIONS = s.SIDE.parent / 'operations'
dependencies = previous.implementation.dependencies
remaining, error = previous.implementation.remaining, previous.implementation.error
inventory, harvest = previous.implementation.inventory, previous.implementation.harvest
MainTermination = previous.implementation.MainTermination


def alarm(deadline):
    signal.setitimer(signal.ITIMER_REAL, max(.001, deadline - time.time()))


def admit_complete_capture():
    terminal = s.read(PREVIOUS_OUTPUT / 'OWNER_TERMINAL.json')
    if not terminal['released'] or terminal['active_unreleased_service'] is not None:
        raise ValueError('previous recovery must release its service')
    if (PREVIOUS_OUTPUT / 'training').exists() or (s.ORIGINAL_ATTEMPT / 'training').exists():
        raise ValueError('training-only continuation requires zero prior training')
    elapsed = []
    for operation, job in (
        ('2026-09-10-after-bounded-question-sensitive-sft', 'question_sensitive_sft72'),
        ('2026-09-10-after-child76-question-sensitive-recovery', 'question_sensitive_recovery_v4'),
    ):
        receipt = s.read(OPERATIONS / operation / 'attempt-001' / job / 'EXIT.json')
        if receipt['gpu_pids_after_exit']:
            raise ValueError('previous parent did not observe an empty GPU')
        elapsed.append(receipt['elapsed_seconds'])
    if sum(elapsed) + 4800 > 10800:
        raise ValueError('combined10800 active ceiling')
    teachers = s.corpus()
    if len(teachers) != 72:
        raise ValueError('complete72 fixed teachers required')
    return dict(teachers=72, original_and_recovery_outer_seconds=elapsed,
                corpus_sha256=s.sha(PREVIOUS_OUTPUT / 'capture/CORPUS_READY.json'),
                new_capture_calls=0, prior_training_updates=0)


def cost_ledger(output):
    result = usage.cost_ledger(output)
    old = s.read(PREVIOUS_OUTPUT / 'COST_LEDGER.json')['by_stage']['recovery_missing_capture']
    for path, pin in old['files_sha256'].items():
        if s.sha(path) != pin:
            raise ValueError('previous capture cost artifact changed')
    result['by_stage']['recovery_missing_capture'] = old
    result['capture_source'] = str(PREVIOUS_OUTPUT)
    result['training_only_continuation'] = True
    return result


def verify():
    value = s.read(s.SOURCE_ROOT / 'POSTCAPTURE_READY.json')
    if s.digest({k: v for k, v in value.items() if k != 'identity'}) != value['identity']:
        raise ValueError('owner amendment identity')
    for path, pin in value['files_sha256'].items():
        if s.sha(path) != pin:
            raise ValueError('postcapture source/input changed: ' + path)
    return dict(amendment_identity=value['identity'], science_identity=s.verify()['identity'],
                admission=admit_complete_capture())


def execute(output):
    output = Path(output)
    started = time.time()
    work, owned = started + 4620, started + 4770
    if output.resolve() != POSTCAPTURE_OUTPUT.resolve() or output.exists():
        raise ValueError('exact unused training-only output required')
    s.runtime()
    ready = s.verify()
    baseline = s.baseline_reference()
    admission = admit_complete_capture()
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('one assigned GPU and private credential required')
    suite = dependencies()
    output.mkdir(parents=True)
    s.write(output / 'CAPTURE_REFERENCE.json', admission)
    s.write(output / 'BASELINE_REFERENCE.json', baseline)
    planned = inventory(output)
    s.write(output / 'PLANNED_EVALUATION.json', planned)
    s.write(output / 'OWNER_RUN.json', dict(identity=ready['identity'], started_epoch=started,
        outer_seconds=4800, owned_seconds=4770, work_seconds=4620,
        stage_caps=dict(training=2100, sft6=2100, finalize=420), new_capture_calls=0,
        original_baseline_reused=True, fresh_optimizer=True, updates=6))
    errors, stages = [], []
    active = None

    def expired(sig, frame):
        if sig in (signal.SIGTERM, signal.SIGINT):
            raise MainTermination('MAIN termination')
        raise TimeoutError('training-only shared/stage cap')

    handlers = {sig: signal.signal(sig, expired)
                for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM)}
    try:
        stage = output / 'train-stage'
        stage.mkdir()
        end = min(time.time() + 2100, work - 2520)
        status = dict(stage='training', started_epoch=time.time(), deadline_epoch=end)
        try:
            argv = [str(s.TRAIN), str(s.SOURCE_ROOT / 'recovery_train_v3.py'), '--mode',
                    'train', '--output', str(output / 'training'), '--deadline', str(end)]
            alarm(end)
            suite.command(stage, 'six-updates', argv, remaining(end), end)
            b.selected('sft6')
            status['work_complete'] = True
        except BaseException as caught:
            status['error'] = error(caught)
            errors.append(dict(stage='training', **status['error']))
        finally:
            status['ended_epoch'] = time.time()
            s.write(stage / 'PHASE_TERMINAL.json', status)
            stages.append(status)
            alarm(owned)
        if status.get('work_complete'):
            stage = output / 'service-sft6'
            stage.mkdir()
            active = stage
            service_started = time.time()
            end = min(service_started + 2100, work - 420)
            status = dict(stage='service-sft6', started_epoch=service_started, deadline_epoch=end)
            try:
                startup = min(time.time() + 180, end - 90)
                alarm(startup)
                suite.start_service(stage, b.binding('sft6'), startup)
                common = ['--binding', str(stage / 'BINDING.json'), '--endpoint',
                          str(stage / 'service/endpoint-original.json')]

                def argv_for(plan, stop, panel, deadline):
                    return [str(s.NATIVE), str(s.SOURCE_ROOT / 'postcapture_readout.py'),
                            '--plan', plan, '--stop', str(stop), *common, '--output',
                            str(output / 'sft6' / panel), '--deadline', str(deadline)]

                dev_started = time.time()
                dev_end = min(dev_started + 150, end - 90)
                try:
                    alarm(dev_end)
                    suite.command(stage, 'dev8', argv_for('DEV_PLAN.json', 8, 'dev', dev_end),
                                  remaining(dev_end), dev_end)
                except Exception as caught:
                    errors.append(dict(stage='sft6-dev', **error(caught)))
                dev_elapsed = time.time() - dev_started
                protected = min(end - 90, service_started + 1950 + dev_elapsed - 90)
                status.update(dev_elapsed_seconds=dev_elapsed,
                              protected_collection_deadline_epoch=protected)
                alarm(protected)
                suite.command(stage, 'protected72',
                    argv_for('FREE_PLAN.json', 72, 'free', protected), remaining(protected), protected)
                status['work_complete'] = True
            except BaseException as caught:
                status['error'] = error(caught)
                errors.append(dict(stage='service-sft6', **status['error']))
            finally:
                alarm(min(owned, end, time.time() + 90))
                try:
                    suite.release_service(stage)
                    active = None
                except BaseException as caught:
                    status['release_error'] = error(caught)
                    errors.append(dict(stage='release', **status['release_error']))
                status['ended_epoch'] = time.time()
                s.write(stage / 'PHASE_TERMINAL.json', status)
                stages.append(status)
    finally:
        alarm(min(owned, time.time() + 420))
        rows = harvest(output, planned)
        s.write(output / 'COST_LEDGER.json', cost_ledger(output))
        result = dict(identity=ready['identity'], complete=not errors and all(r['recorded'] for r in rows),
            error=errors or None, readout_inventory=rows, baseline_reference=baseline,
            capture_reference=admission, stages=stages, released=active is None,
            active_unreleased_service=str(active) if active else None,
            elapsed_seconds=time.time() - started, planned_readout=80, new_capture_calls=0)
        s.write(output / 'OWNER_TERMINAL.json', result)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return result


implementation = sys.modules[__name__]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run'))
    parser.add_argument('--output', type=Path, default=POSTCAPTURE_OUTPUT)
    args = parser.parse_args()
    checked = verify()
    if args.command == 'verify':
        print(checked)
    else:
        result = execute(args.output)
        print(dict(complete=result['complete'], released=result['released']))
        raise SystemExit(0 if result['complete'] else 1)
