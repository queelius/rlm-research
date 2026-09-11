"""Exact equal-row control identities and exposed fresh-seed readout coordinates."""
import contextlib
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / 'root-interface-sft-v1'
LOCAL = ROOT.parent / 'root-interface-sft-local-runtime-v1'
CONTROL = LOCAL / 'outputs/attempt-001/training'
NATIVE = Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
TRAIN = Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
PRIOR_IDENTITY = '256473666b3f67b007b8a8acbad5150b468cbbff2ec2981ad8320786668cced8'
CONTROL_SHA = 'efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64'
CHILD_SHA = 'c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3'
BASE_SHA = '19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f'
PHASES = ('equal_row', 'global_target_token')
PINS = {PRIOR / 'READY.json': '397f3ccc6c701f31ac2702383839d6cdee7de621d7fa91bcac748f828734789a',
        PRIOR / 'train.py': 'b333d787bde61b9f42cd5bfba426dd3909d5733a4ea55ae693f547ca429597a7',
        LOCAL / 'READY.json': '77df23b82890e9793eb41e78324beeb67b05a44ad134251d6507ed19cba8c3ed',
        LOCAL / 'adapter.py': '8ea5aef6f69f358814baa6a3d6fb5ce5fcc12418fa45910b85dd99faded8c298',
        ROOT / 'DESIGN.md': '7eae8fc877fb7e74530c76eda41cc636bc55c1177fa6dc91cd3f8195fdd24f4f',
        ROOT / 'PLAN.md': '2aa97a648a4c90efd04fc9997daa47d6b5eb6b77a25dda0769df79048579c167',
        ROOT / 'WEIGHTING_AND_SEED_AUDIT.json': 'd3f62362fa82f26215c7264d962f774a0d952c94b6790f82463ae693eddbb39f'}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def check(path, expected):
    if sha(path) != expected:
        raise ValueError('frozen identity changed: ' + str(path))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


@contextlib.contextmanager
def aliases(mapping):
    previous = {key: sys.modules.get(key) for key in mapping}
    sys.modules.update(mapping)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value


def load(name, path, expected):
    check(path, expected)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def prior():
    check(PRIOR / 'READY.json', PINS[PRIOR / 'READY.json'])
    return load('rowmean_original_study', PRIOR / 'study.py', read(PRIOR / 'READY.json')['source_sha256'][str(PRIOR / 'study.py')])


@functools.lru_cache(maxsize=1)
def stack():
    old = prior()
    sources = read(PRIOR / 'READY.json')['source_sha256']
    with aliases({'study': old}):
        native = load('rowmean_original_native', PRIOR / 'native.py', sources[str(PRIOR / 'native.py')])
        interface = load('rowmean_original_interface', PRIOR / 'interface.py', sources[str(PRIOR / 'interface.py')])
    native.e.fixture_task = functools.lru_cache(maxsize=1)(native.e.fixture_task)
    local = load('rowmean_exact_local_runtime', LOCAL / 'adapter.py', PINS[LOCAL / 'adapter.py'])
    return SimpleNamespace(prior=old, native=native, interface=interface, local=local)


def build_plan(original):
    first = {'validation': 981300101, 'query_transfer': 981300201, 'length_transfer': 981300301}
    counts = dict.fromkeys(first, 0)
    plan = []
    for old in original:
        stratum = old['stratum']
        row = {**old, 'source_coordinate_id': old['id'], 'seed': first[stratum] + counts[stratum]}
        row.pop('id')
        row['id'] = digest(row)
        plan.append(row)
        counts[stratum] += 1
    if counts != dict.fromkeys(first, 8):
        raise ValueError('exact24 source coordinates required')
    return plan


@functools.lru_cache(maxsize=4)
def checkpoint(training, expected_identity, expected_adapter=None):
    training = Path(training)
    result = read(training / 'RESULT.json')
    selected = result['selected']
    path = Path(selected['checkpoint'])
    if (not result['complete'] or selected['step'] != 4 or path != training / 'checkpoint-0004'
            or result['identity'] != expected_identity or result['starting_adapter_sha256'] != prior().START_SHA
            or not result['fresh_optimizer'] or result['child_loaded'] or result['child_updated']
            or result['record_exposures'] != 64 or result['target_token_exposures'] != 3206
            or read(training / 'SELECTION.json') != selected):
        raise ValueError('not the exact fixed-final4 SFT lineage')
    if expected_adapter is not None and selected['adapter_sha256'] != expected_adapter:
        raise ValueError('control adapter changed')
    check(path / 'state.json', selected['state_sha256'])
    state = read(path / 'state.json')
    if ((state['step'], state['epoch'], state['cursor']) != (4, 2, 0)
            or state['identity'] != expected_identity or state['files_sha256'] != result['files_sha256']):
        raise ValueError('checkpoint cursor/identity differs')
    for name, expected in state['files_sha256'].items():
        if Path(name).name != name:
            raise ValueError('invalid checkpoint member')
        check(path / name, expected)
    if (selected['adapter_sha256'] != state['files_sha256']['adapter_model.safetensors']
            or selected['config_sha256'] != state['files_sha256']['adapter_config.json']):
        raise ValueError('adapter/config closure mismatch')
    return selected


def binding(arm, training, selected):
    if arm not in PHASES:
        raise ValueError('unknown fixed arm')
    result = stack().native.initial_binding()
    result['models'].pop(result['role_map']['root'])
    alias = 'strict-rlm-qwen3-4b-root-' + ('rowmean' if arm == 'equal_row' else 'interface') + '-final4-v1'
    model = {'path': selected['checkpoint'], 'adapter_sha256': selected['adapter_sha256'], 'config_sha256': selected['config_sha256']}
    result['models'][alias] = model
    result['role_map']['root'] = alias
    result['campaign_policy'] = {**model, 'step': 4, 'state_sha256': selected['state_sha256'],
        'optimizer_sha256': read(training / 'RESULT.json')['files_sha256']['optimizer.pt'],
        'rng_sha256': read(training / 'RESULT.json')['files_sha256']['rng_state.pt']}
    result['campaign_id'] = ROOT.name
    result.pop('receipt_uptake_study', None)
    result['selection_path'] = str(training / 'SELECTION.json')
    result['selection_sha256'] = sha(training / 'SELECTION.json')
    result['selection_semantics'] = 'fixed-final4; same473210 and fresh Adam; no validation selection'
    result['loss_weighting_readout'] = {'study': ROOT.name, 'arm': arm, 'training_result_sha256': sha(training / 'RESULT.json')}
    if result['models'][result['fixed_child']]['adapter_sha256'] != CHILD_SHA:
        raise ValueError('fixed child changed')
    return result


def validate_binding(actual, arm, training, selected):
    if actual != binding(arm, training, selected):
        raise ValueError('exact current root/child binding differs')


@functools.lru_cache(maxsize=1)
def verify():
    ready = read(ROOT / 'READY.json')
    manifest = {k: v for k, v in ready.items() if k != 'identity'}
    if digest(manifest) != ready['identity']:
        raise ValueError('source manifest identity differs')
    for path, expected in {**ready['source_sha256'], **ready['input_sha256']}.items():
        check(path, expected)
    return ready
