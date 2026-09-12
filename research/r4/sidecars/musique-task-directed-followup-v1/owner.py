"""MAIN-only service ownership; exact science/cleanup deadlines and additive telemetry."""
import argparse
import json
import os
import signal
import time

import collect
import metrics
import study


def start_attestation(directory):
    start = study.read(directory / 'SERVER_START.json')
    actual = study.read(directory / 'ENGINE_ENV_ATTESTATION.json')
    base_digest = study.base_owner().study.digest
    expected = {'schema': 'batch-invariant-engine-preexec-attestation-v1', 'pid': start['pid'],
        'VLLM_BATCH_INVARIANT': '1', 'command_sha256': base_digest(start['command']),
        'wrapper_sha256': study.sha(study.ROOT / 'service_wrapper.py'), 'credentials_persisted': False}
    assert actual == expected and start['launcher_sha256'] == expected['wrapper_sha256']
    return actual


def qualify_dispatch(service, start, released):
    assert released
    path = service / 'service/ACTUAL_DISPATCH.json'
    receipt = study.read(path)
    assert receipt['schema'] == 'first-real-eager-batch-invariant-dispatch-v1'
    assert receipt['environment_flag'] == '1' and receipt['resolved_flag'] is True
    assert receipt['installed_batch_invariant_mode'] is True and receipt['device_type'] == 'cuda'
    assert receipt['original_function_returned'] is True and receipt['tensor_values_or_credentials_persisted'] is False
    assert receipt['instrumentation_sha256'] == study.sha(study.ROOT / 'report_worker.py')
    assert receipt['kernel_source_sha256'] == study.sha(receipt['kernel_source'])
    assert receipt['kernel_source_sha256'] == study.read(study.ROOT / 'READY.json')['closure_sha256'][receipt['kernel_source']]
    # EngineCore PID association uses safe process/log metadata, not a warning.
    log = service / 'service/inference.log'
    assert '(EngineCore pid=' + str(receipt['pid']) + ')' in log.read_text()
    assert any(study.read(p).get('process', {}).get('pid') == receipt['pid'] for p in (service / 'OWNED_PROCESSES').glob('*.json'))
    return {'preexec': start, 'dispatch': receipt, 'dispatch_receipt_sha256': study.sha(path),
            'inference_log_sha256': study.sha(log), 'released': True,
            'optional_Dynamo_warning_required': False, 'no_bitwise_invariance_claim': True}


def execute(seconds):
    ready = study.verify()
    if seconds != study.OWNER_SECONDS or study.ATTEMPT.exists(): raise ValueError('exact cap and unused attempt required')
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('MAIN owned GPU/credential required')
    started = time.time(); end = started + seconds
    study.ATTEMPT.mkdir(parents=True)
    service = study.ATTEMPT / 'service'; service.mkdir()
    base = study.base_owner(); binding = base.study.binding()
    study.write_x(study.ATTEMPT / 'BINDING.json', binding)
    study.write_x(study.ATTEMPT / 'OWNER_RUN.json', {'ready_identity': ready['identity'],
        'ready_sha256': study.sha(study.ROOT / 'READY.json'), 'started_epoch': started,
        'owner_seconds': seconds, 'science_seconds': study.SCIENCE_SECONDS, 'planned_calls': 132,
        'planned_final_slots': 48, 'optimizer_steps': 0})
    def interrupted(sig, frame): raise TimeoutError('owner interrupted ' + str(sig))
    previous = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGALRM, signal.SIGINT, signal.SIGTERM)}
    signal.setitimer(signal.ITIMER_REAL, seconds - 30)
    errors, phases, suite, released, start = [], {}, None, False, None
    qualified = False
    try:
        suite = base.study.dependencies()
        suite.SERVE = study.ROOT / 'service_wrapper.py'
        suite.life.__dict__['ALLOCATION_SERVICE'] = suite.SERVE
        suite.start_service(service, binding, min(started + 285, end - 90))
        assert study.read(service / 'BINDING.json') == binding == study.read(service / 'service/BINDING.json')
        config = study.read(service / 'service/inference.json')
        assert config['vllm']['enable_lora'] is False and config['vllm']['enable_prefix_caching'] is False
        assert config['vllm']['enforce_eager'] is True and config['vllm']['max_model_len'] == 8192
        assert config['vllm']['max_num_seqs'] == 4 and config['vllm']['worker_extension_cls'] == 'report_worker.ReportWorker'
        study.write_x(study.ATTEMPT / 'RUNTIME.json', base.study.sanitized_runtime(config))
        start = start_attestation(service / 'service')
        # Warmup must already have supplied actual worker dispatch evidence.
        assert (service / 'service/ACTUAL_DISPATCH.json').exists()
        descriptor = study.read(service / 'service/endpoint-original.json')
        endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        phases['service_startup_seconds'] = time.time() - started
        science_started = time.time()
        collected = collect.execute(endpoint, study.ATTEMPT, min(science_started + study.SCIENCE_SECONDS, end - 90))
        phases['science_elapsed_seconds'] = time.time() - science_started
        errors.extend(collected['errors'])
    except Exception as error:
        errors.append({'stage': 'owner', 'type': type(error).__name__})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 60)
        cleanup = time.time()
        if suite is not None:
            try:
                suite.release_service(service)
                stopped = study.read(service / 'SERVICE_STOPPED.json')
                released = bool(stopped['all_owned_process_identities_exited'] and stopped['ports_free'])
            except Exception as error: errors.append({'stage': 'release', 'type': type(error).__name__})
        else: released = True
        if start is not None and released:
            try:
                attested = qualify_dispatch(service, start, released)
                study.write_x(study.ATTEMPT / 'ENGINE_ATTESTATION.json', attested); qualified = True
            except Exception as error: errors.append({'stage': 'dispatch_qualification', 'type': type(error).__name__})
        phases['cleanup_seconds'] = time.time() - cleanup
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items(): signal.signal(sig, handler)
    result = metrics.summarize(study.ATTEMPT, qualified)
    result.update(phases=phases, errors=errors, released=released)
    study.write_x(study.ATTEMPT / 'RESULT.json', result)
    terminal = {'complete': result['complete'] and not errors and released, 'runtime_qualified': qualified,
                'released': released, 'elapsed_seconds': time.time() - started, 'errors': errors,
                'result_sha256': study.sha(study.ATTEMPT / 'RESULT.json')}
    study.write_x(study.ATTEMPT / 'OWNER_TERMINAL.json', terminal)
    return terminal


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['verify', 'run'])
    parser.add_argument('--outer-seconds', type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == 'verify': print(study.verify()['identity'])
    else:
        value = execute(args.outer_seconds); print(json.dumps(value)); raise SystemExit(0 if value['complete'] else 1)
