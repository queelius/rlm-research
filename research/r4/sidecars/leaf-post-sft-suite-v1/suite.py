"""One parent-launched, two-service post-SFT suite; no implicit retries or new cells."""
import argparse
import copy
import fcntl
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
CAMPAIGN = SIDE/'root-rlvr-campaign-v1'
LIFECYCLE_SHA = '568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5'
SENTIMENT = SIDE/'leaf-sentiment-transfer-v1'
CONTROLS = SIDE/'leaf-correspondence-controls-v1'
OPTIONAL = SIDE/'leaf-mixed-size-schema-control-v1'
SENTIMENT_SHA = 'eb9509ed00a85cd942d959407deb8c80f495f7fec2426f477265af48e407cb63'
sys.path.insert(0, str(CAMPAIGN))
import campaign_common as c
c.authenticate({CAMPAIGN/'campaign_lifecycle_v2.py': LIFECYCLE_SHA})
import campaign_lifecycle_v2 as life
c.authenticate({SENTIMENT/'driver.py': SENTIMENT_SHA})
sentiment = c.load('post_suite_sentiment', SENTIMENT/'driver.py')
PYTHON = str(c.NATIVE_PYTHON)
SERVE = c.ROLE/'source/serve.py'
LAUNCHERS = {}


def jobs(stage, include_optional=False):
    if stage == 'original_old':
        result = [{'kind': 'correspondence', 'condition': name, 'endpoint': 'endpoint-selected.json'}
                for name in ('representation', 'rotation')] + [
            {'kind': 'sentiment', 'condition': 'original', 'endpoint': 'endpoint-original.json'},
            {'kind': 'sentiment', 'condition': 'old_sft', 'endpoint': 'endpoint-selected.json'}]
    elif stage == 'mixed_ab':
        result = [{'kind': 'sentiment', 'condition': name, 'endpoint': filename}
                for name, filename in [('A', 'endpoint-original.json'), ('B', 'endpoint-selected.json')]]
    else:
        raise ValueError('unknown fixed suite stage')
    expanded = []
    for row in result:
        expanded.append(row)
        if include_optional and row['kind'] == 'sentiment':
            expanded.append({**row, 'kind': 'mixed_schema',
                'condition': {'A': 'Afinal', 'B': 'Bfinal'}.get(row['condition'], row['condition'])})
    return expanded


def final_binding(models, decision_path):
    aliases = list(models)
    if len(aliases) != 2:
        raise ValueError('exactly two fixed final adapters required')
    return {'schema': 'fixed-final-epoch2-dual-leaf-binding-v1', 'models': models,
            'role_map': {'root': aliases[0], 'children': aliases},
            'selection_path': str(decision_path), 'selection_sha256': c.file_hash(decision_path),
            'selection_semantics': 'Fixed final epoch2 for both arms; no validation or transfer selection',
            'post_training_test_consulted_for_binding': False}


def prepare_bindings(output):
    old_path = c.ROLE/'BOUND_WEIGHTS.json'
    old = c.read(old_path)
    descriptor = c.read(c.ROLE/'service-attempt-001/endpoint-original.json')
    closure = {str(old_path): c.file_hash(old_path)}
    for condition, alias in [('original', old['role_map']['root']), ('old_sft', 'strict-rlm-qwen3-4b-role-sft-selected-v1')]:
        model = old['models'][alias]
        endpoint = {**descriptor, 'model_alias': alias, 'adapter': {'path': model['path'],
            'model_sha256': model['adapter_sha256'], 'config_sha256': model['config_sha256']}}
        sentiment.authenticate_weight(condition, endpoint, closure)
    models = {}
    for arm, step in [('A', 206), ('B', 204)]:
        checkpoint = SIDE/'leaf-mixed-size-sft-v1'/arm/'outputs/attempt-001'/f'checkpoint-{step:04d}'
        alias = f'strict-rlm-qwen3-4b-leaf-mixed-{arm.lower()}-final-v1'
        model = {'path': str(checkpoint), 'adapter_sha256': c.file_hash(checkpoint/'adapter_model.safetensors'),
                 'config_sha256': c.file_hash(checkpoint/'adapter_config.json')}
        endpoint = {**descriptor, 'model_alias': alias, 'adapter': {'path': model['path'],
            'model_sha256': model['adapter_sha256'], 'config_sha256': model['config_sha256']}}
        sentiment.authenticate_weight(arm, endpoint, closure)
        models[alias] = model
    decision = {'schema': 'post-sft-fixed-final-decision-v1', 'rule': 'Fixed final epoch2; not validation-selected',
                'models': models, 'source_sha256': closure, 'transfer_outcomes_consulted': False,
                'checkpoint_steps': {'A': 206, 'B': 204}}
    decision_path = output/'FIXED_FINAL_DECISION.json'
    c.write_once(decision_path, decision)
    c.write_once(output/'INPUT_BINDING_AUDIT.json', {'source_sha256': closure,
        'original_and_old_sft': old, 'fixed_final': decision, 'gpu_calls': 0})
    return {'original_old': old, 'mixed_ab': final_binding(models, decision_path)}


def budget(deadline, cap):
    left = deadline-time.time()
    if left <= 0:
        raise TimeoutError('suite two-hour envelope exhausted; no new commands')
    return min(left, cap)


def stop_child(process, observation):
    """Popen child only, authenticated by V2 stable identity before every group signal."""
    for sig, seconds in [(signal.SIGINT, 10), (signal.SIGTERM, 5), (signal.SIGKILL, 5)]:
        if process.poll() is not None:
            return
        actual = life.observe(process.pid)
        if not life.same_process(observation, actual):
            raise ValueError('owned launcher identity changed; refusing group signal')
        os.killpg(observation['pgid'], sig)
        try:
            process.wait(timeout=seconds)
            return
        except subprocess.TimeoutExpired:
            pass
    raise RuntimeError('owned command failed to release')


def observe_service(directory):
    if directory in LAUNCHERS:
        _, parent = LAUNCHERS[directory]
        life.snapshot_descendants(directory/'service', parent)
    return life.claim_service(directory/'service')


def start_service(directory, binding, deadline):
    if not life.v1.ports_free():
        raise ValueError('service ports occupied; no unrelated cleanup authorized')
    binding_path = directory/'BINDING.json'
    c.write_once(binding_path, binding)
    service = directory/'service'
    command = [PYTHON, str(SERVE), '--binding', str(binding_path), '--run-dir', str(service)]
    c.write_once(directory/'SERVICE_REQUEST.json', {'command': command, 'gpu': os.environ['CUDA_VISIBLE_DEVICES'],
        'suite_manifest_sha256': c.file_hash(ROOT/'MANIFEST.json')})
    with (directory/'launcher.log').open('x') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                   env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, start_new_session=True)
    observation = life.observe(process.pid)
    if observation is None or observation['pgid'] != process.pid or observation['uid'] != os.getuid():
        raise ValueError('cannot authenticate newly created suite launcher')
    LAUNCHERS[directory] = (process, life.safe_observation(observation))
    c.write_once(directory/'LAUNCHER_PROCESS.json', life.safe_observation(observation))
    until = time.time()+budget(deadline, 600)
    while time.time() < until:
        observe_service(directory)
        if process.poll() is not None:
            if process.returncode or not (service/'SERVER_READY.json').exists():
                raise RuntimeError('dual-LoRA launcher failed; see retained log')
            preflight(service, binding)
            return
        time.sleep(.5)
    raise TimeoutError('owned service readiness cap reached')


def release_service(directory):
    # Stop only this still-running launcher before stopping its authenticated service.
    if directory in LAUNCHERS:
        process, observation = LAUNCHERS[directory]
        life.snapshot_descendants(directory/'service', observation)
        stop_child(process, observation)
    life.stop_service(directory/'service')
    LAUNCHERS.pop(directory, None)


def preflight(service, binding):
    import httpx
    endpoint = c.read(service/'endpoint-original.json')
    config = c.read(service/'inference.json')['vllm']
    if config.get('max_model_len') != 8192 or config.get('lora_dtype') != 'auto':
        raise ValueError('inference context/cast configuration changed')
    key = os.environ[endpoint['api_key_env']]
    url = f"http://{endpoint['host']}:{endpoint['port']}"
    with httpx.Client(headers={'Authorization': 'Bearer '+key}, trust_env=False, timeout=30) as client:
        response = client.get(url+'/version')
        response.raise_for_status()
        version = response.json()
        if version.get('version') != '0.28.0':
            raise ValueError('unqualified inference version')
        response = client.get(url+'/v1/models')
        response.raise_for_status()
        models = response.json()
    cards = {r['id']: r for r in models['data']}
    for alias, model in binding['models'].items():
        if alias not in cards or cards[alias].get('root') != model['path'] or cards[alias].get('parent') != endpoint['base_model']['path']:
            raise ValueError('live alias/adapter/base mismatch')
    c.write_once(service.parent/'SUITE_PREFLIGHT.json', {'version': version, 'models': models,
        'inference_sha256': c.file_hash(service/'inference.json'), 'checked_epoch': time.time()})


def command(directory, label, argv, cap, deadline):
    remaining = budget(deadline, cap)
    c.write_once(directory/(label+'-COMMAND.json'), {'argv': argv, 'cap_seconds': remaining,
        'started_epoch': time.time(), 'service_owner_path': str(directory/'SERVICE_OWNER_V2.json'),
        'gpu_visible_to_command': False})
    environment = {**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'}
    with (directory/(label+'.log')).open('x') as log:
        process = subprocess.Popen(argv, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    observed = life.observe(process.pid)
    if observed is None or observed['pgid'] != process.pid or observed['uid'] != os.getuid():
        raise ValueError('cannot authenticate newly created evaluation child')
    observation = life.safe_observation(observed)
    c.write_once(directory/(label+'-PROCESS.json'), observation)
    until = time.time()+remaining
    try:
        while process.poll() is None:
            observe_service(directory)
            if time.time() >= until:
                raise TimeoutError('bounded suite command exhausted its cap')
            time.sleep(.5)
        if process.returncode:
            raise RuntimeError(f'{label} exited{process.returncode}; retained log')
    finally:
        stop_child(process, observation)
        c.write_once(directory/(label+'-EXIT.json'), {'returncode': process.returncode, 'ended_epoch': time.time()})


def run_jobs(directory, stage, deadline):
    optional = c.read(directory.parent/'OPTIONAL_CONTROL.json')
    if optional['status'] == 'ready-bound-at-suite-start':
        c.authenticate(optional['source_sha256'])
    for item in jobs(stage, optional['status'] == 'ready-bound-at-suite-start'):
        name = item['kind']+'-'+item['condition']
        endpoint = directory/'service'/item['endpoint']
        spec_path = directory/(name+'-BOUND.json')
        output = directory/'outputs'/name
        if item['kind'] == 'correspondence':
            script = CONTROLS/'driver.py'
            bind = [PYTHON, str(script), 'bind', '--comparison', item['condition'],
                    '--endpoint-descriptor', str(endpoint), '--spec-path', str(spec_path)]
            run = [PYTHON, str(script), 'run', '--spec-path', str(spec_path), '--output-dir', str(output)]
            cap = 330
        elif item['kind'] == 'sentiment':
            script = SENTIMENT/'driver.py'
            bind = [PYTHON, str(script), 'bind', '--condition', item['condition'],
                    '--endpoint', str(endpoint), '--output', str(spec_path)]
            run = [PYTHON, str(script), 'run', '--spec', str(spec_path), '--output', str(output)]
            cap = 1230
        else:
            script = OPTIONAL/'driver.py'
            bind = [PYTHON, str(script), 'bind', '--weight', item['condition'],
                    '--endpoint-descriptor', str(endpoint), '--spec-path', str(spec_path)]
            run = [PYTHON, str(script), 'run', '--spec-path', str(spec_path), '--output-dir', str(output)]
            cap = 630
        command(directory, name+'-bind', bind, 120, deadline)
        command(directory, name+'-run', run, cap, deadline)


def execute_stage(directory, binding, stage, deadline):
    directory.mkdir(parents=True, exist_ok=False)
    c.write_once(directory/'STAGE_PLAN.json', {'stage': stage, 'jobs': jobs(stage), 'binding': binding})
    try:
        start_service(directory, binding, deadline)
        run_jobs(directory, stage, deadline)
    except BaseException as error:
        c.write_once(directory/'STAGE_ERROR.json', {'error_type': type(error).__name__, 'error': str(error), 'time': time.time()})
        raise
    finally:
        try:
            release_service(directory)
        except BaseException as error:
            c.write_once(directory/'RELEASE_ERROR.json', {'error_type': type(error).__name__, 'error': str(error), 'time': time.time()})
            raise
    c.write_once(directory/'STAGE_COMPLETE.json', {'stage': stage, 'completed_epoch': time.time(), 'owned_service_released': True})


def verify():
    manifest = c.read(ROOT/'MANIFEST.json')
    if c.digest({k: v for k, v in manifest.items() if k != 'identity'}) != manifest['identity']:
        raise ValueError('suite manifest identity changed')
    c.authenticate(manifest['source_sha256'])
    life.verify_amendment()
    frozen = c.read(SENTIMENT/'SPEC.json')
    sentiment.checked_identity(frozen)
    c.authenticate(frozen['source_sha256'])
    return manifest


def seal():
    """CPU source closure only; no outcome selection or live contact."""
    amendment = life.verify_amendment()
    controls_ready = c.read(CONTROLS/'READY.json')
    paths = [Path(__file__), ROOT/'test_suite.py', ROOT/'DESIGN.md', ROOT/'PLAN.md',
        SENTIMENT/'READY.json', SENTIMENT/'SPEC.json', CONTROLS/'READY.json',
        CONTROLS/'driver.py', SERVE, c.ROLE/'source/routing.py', c.ROLE/'BOUND_WEIGHTS.json',
        c.ROLE/'service-attempt-001/endpoint-original.json', life.AMENDMENT,
        SIDE/'strict-rlm-temperature-adherence-v1/scripts/launch.py',
        SIDE/'strict-rlm-temperature-adherence-v1/configs/inference-replica0.json',
        SIDE/'strict-rlm-temperature-adherence-v1/configs/endpoint-replica0.json']
    sources = {str(p): c.file_hash(p) for p in paths}
    sources.update(amendment['source_sha256'])
    campaign = c.read(CAMPAIGN/'CAMPAIGN.json')
    sources.update(campaign['source_sha256'])
    sources.update(campaign['input_sha256'])
    sources.update(c.read(SENTIMENT/'SPEC.json')['source_sha256'])
    for name in ['REPRESENTATION', 'ROTATION']:
        path = CONTROLS/f'SPEC-{name}.runtime-order-v2.json'
        sources[str(path)] = c.file_hash(path)
        sources.update(c.read(path)['source_file_sha256'])
    manifest = {'schema': ROOT.name, 'source_sha256': sources,
        'stages': {name: jobs(name) for name in ['original_old', 'mixed_ab']},
        'controls_ready': controls_ready, 'total_primary_calls': 536,
        'global_cap_seconds': 7200, 'work_envelope_seconds': 7080,
        'optional_mixed_schema': {'status': 'bind-once-at-suite-start-if-ready-otherwise-skip',
            'ready_path': str(OPTIONAL/'READY.json'), 'driver_path': str(OPTIONAL/'driver.py'),
            'weights': ['original', 'old_sft', 'Afinal', 'Bfinal'], 'max_additional_calls': 64,
            'bind_cli': 'bind --weight WEIGHT --endpoint-descriptor ACTUAL --spec-path NEW',
            'run_cli': 'run --spec-path BOUND --output-dir NEW'},
        'gpu_calls_during_preparation': 0, 'fixed_final_results_bound_only_at_run_start': True}
    manifest['identity'] = c.digest(manifest)
    c.authenticate(sources)
    c.write_once(ROOT/'MANIFEST.json', manifest)
    print(json.dumps({'identity': manifest['identity'], 'gpu_calls': 0}))


def run(output):
    manifest = verify()
    gpu = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if not gpu or ',' in gpu:
        raise ValueError('parent must explicitly assign exactly one exclusively owned device')
    if not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('parent must supply the qualified local API key environment')
    output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    deadline = started+7080
    c.write_once(output/'RUN.json', {'started_epoch': started, 'global_cap_seconds': 7200,
        'work_deadline_epoch': deadline, 'gpu': gpu, 'manifest': manifest,
        'command': sys.argv, 'python': sys.version, 'lifecycle_v2_amendment_sha256': c.file_hash(life.AMENDMENT)})
    try:
        optional_path = OPTIONAL/'READY.json'
        if optional_path.exists():
            ready = c.read(optional_path)
            hashes = {str(optional_path): c.file_hash(optional_path),
                      str(OPTIONAL/'driver.py'): ready['driver_sha256']}
            c.authenticate(hashes)
            optional = {'status': 'ready-bound-at-suite-start', 'ready': ready,
                        'source_sha256': hashes, 'maximum_calls': 64}
        else:
            optional = {'status': 'skipped-not-ready-at-suite-start', 'checked_path': str(optional_path)}
        c.write_once(output/'OPTIONAL_CONTROL.json', optional)
        bindings = prepare_bindings(output)
        for stage in ['original_old', 'mixed_ab']:
            execute_stage(output/stage, bindings[stage], stage, deadline)
    except BaseException as error:
        c.write_once(output/'ERROR.json', {'error_type': type(error).__name__, 'error': str(error), 'time': time.time()})
        raise
    finally:
        c.write_once(output/'STATUS.json', {'wall_seconds': time.time()-started,
            'completed_stages': [stage for stage in ['original_old', 'mixed_ab'] if (output/stage/'STAGE_COMPLETE.json').exists()],
            'partial_artifacts_retained': True, 'implicit_retries': 0})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['seal', 'verify', 'run'])
    parser.add_argument('--output', type=Path, default=ROOT/'outputs/attempt-001')
    args = parser.parse_args()
    if args.command == 'seal':
        seal()
        return
    if args.command == 'verify':
        print(json.dumps({'identity': verify()['identity'], 'gpu_calls': 0}))
        return
    def interrupted(sig, frame):
        raise KeyboardInterrupt(f'parent signal{sig}; release owned service in finally')
    signal.signal(signal.SIGTERM, interrupted)
    # Shared qualified campaign lease prevents overlapping this suite with that coordinator.
    with (CAMPAIGN/'COORDINATOR.lock').open('a') as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.output.resolve())


if __name__ == '__main__':
    main()
