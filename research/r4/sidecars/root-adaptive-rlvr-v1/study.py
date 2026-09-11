"""Fixed adaptive allocation, coordinates and explicitly approved fresh-Adam start."""
import contextlib
import functools
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PRIOR = SIDE / 'root-interface-sft-v1'
LOCAL = SIDE / 'root-interface-sft-local-runtime-v1'
CAMPAIGN = SIDE / 'root-rlvr-campaign-v1'
NATIVE = Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
TRAIN = Path('/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python')
SEED = 981298001
CHILD_SHA = 'c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3'
HISTORICAL_SHA = '473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd'
PINS = {
    PRIOR / 'READY.json': '397f3ccc6c701f31ac2702383839d6cdee7de621d7fa91bcac748f828734789a',
    PRIOR / 'RECIPE.json': 'bf708ced9d5be9ed7c1dc8ebb1877afb0e786c5633e5de246bafb4b99af57911',
    PRIOR / 'prepared-v2/PUBLIC.json': '8c22ee2d897542cab3863bc402e668db0e76cc4ccd8691398692e7a2571d9f33',
    PRIOR / 'prepared-v2/HOST_GOLD.json': '4c66309be0f2db750553534561fc4ac3a611cc2792175b6140f936aa4de0ddcd',
    LOCAL / 'READY.json': '77df23b82890e9793eb41e78324beeb67b05a44ad134251d6507ed19cba8c3ed',
    LOCAL / 'adapter.py': '8ea5aef6f69f358814baa6a3d6fb5ce5fcc12418fa45910b85dd99faded8c298',
    CAMPAIGN / 'campaign_common.py': '17e888550668638673fa725c6a580b7580b6abd975bd27f69b8be7ad628800ea',
    CAMPAIGN / 'campaign_train.py': '38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f',
}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def check(path, expected):
    if sha(path) != expected:
        raise ValueError('authenticated identity changed: ' + str(path))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


@contextlib.contextmanager
def aliases(mapping):
    before = {k: sys.modules.get(k) for k in mapping}
    sys.modules.update(mapping)
    try:
        yield
    finally:
        for name, value in before.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def load(name, path, expected):
    check(path, expected)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def prior_study():
    check(PRIOR / 'READY.json', PINS[PRIOR / 'READY.json'])
    sources = read(PRIOR / 'READY.json')['source_sha256']
    return load('adaptive_rlvr_pinned_sft_study', PRIOR / 'study.py', sources[str(PRIOR / 'study.py')])


def data():
    for name in ('PUBLIC.json', 'HOST_GOLD.json'):
        path = PRIOR / 'prepared-v2' / name
        check(path, PINS[path])
    return read(PRIOR / 'prepared-v2/PUBLIC.json'), read(PRIOR / 'prepared-v2/HOST_GOLD.json')


def coordinate(context, family, repeat, seed, split):
    row = dict(context_id=context['id'], context_window_id=prior_study().context_window_id(context),
               task_name='adaptive-' + context['id'] + '-' + family, family=family,
               stratum=context['stratum'], split=split, repeat=repeat, seed=seed,
               records=len(context['records']), arm='typed', temperature=.5, client_path='train')
    row['id'] = digest(row)
    return row


def build_plans(public):
    training = sorted((c for c in public if c['stratum'] == 'train'), key=lambda c: c['id'])
    if [len(c['records']) for c in training] != [32] * 4 + [64] * 4:
        raise ValueError('exact frozen training allocation changed')
    plans = {'training': {}, 'validation': [], 'transfer': []}
    for step in range(1, 9):
        i = (step - 1) % 4
        small_single = (i % 2 == 0) != (step > 4)
        families = ('single_user', 'global') if small_single else ('global', 'single_user')
        plans['training'][str(step)] = [coordinate(training[i + slot * 4], families[slot], repeat,
                981298100 + (step - 1) * 16 + repeat * 2 + slot, 'training')
            for repeat in range(8) for slot in range(2)]
    for stratum, families, repeats, first in [
        ('validation', ('single_user', 'global'), 1, 981298500),
        ('query_transfer', ('single_user', 'two_user_union'), 2, 981298600),
        ('length_transfer', ('single_user', 'global'), 2, 981298700),
    ]:
        rows = []
        for context in sorted((c for c in public if c['stratum'] == stratum), key=lambda c: c['id']):
            for family in families:
                for repeat in range(repeats):
                    rows.append(coordinate(context, family, repeat, first + len(rows), stratum))
        plans['validation' if stratum == 'validation' else 'transfer'].extend(rows)
    return plans


def endpoint_reward(reply, gold, completed, available):
    if not completed or not available or not isinstance(reply, str):
        return None
    match = re.fullmatch(r'Answer: ([0-9]+)', reply.strip())
    return int(match is not None and int(match.group(1)) == gold)


def fresh_policy(model):
    return {'step': 0, **{k: model[k] for k in ('path', 'adapter_sha256', 'config_sha256')},
            'optimizer_sha256': None, 'rng_sha256': None, 'state_sha256': None}


def authenticate_start(value):
    if value.get('approved') is not True or value.get('decision_by') != 'MAIN':
        raise ValueError('MAIN must explicitly approve the immutable starting identity')
    if value.get('campaign_sha256') != sha(ROOT / 'CAMPAIGN.json'):
        raise ValueError('starting decision belongs to a different campaign')
    model = value['model']
    if value['kind'] == 'historical473210':
        prior = prior_study()
        recipe = read(PRIOR / 'RECIPE.json')
        expected = {'path': str(prior.START), 'adapter_sha256': HISTORICAL_SHA,
                    'config_sha256': recipe['starting_files_sha256']['adapter_config.json']}
        evidence = {str(prior.START / name): h for name, h in recipe['starting_files_sha256'].items()}
        if model != expected:
            raise ValueError('historical warm start is not the exact named checkpoint')
    elif value['kind'] == 'interface_sft_final4':
        result_path = Path(value['result_path'])
        if result_path != LOCAL / 'outputs/attempt-001/training/RESULT.json':
            raise ValueError('SFT result is not the exact accepted local-runtime training attempt')
        result = read(result_path)
        selected = result['selected']
        checkpoint = Path(selected['checkpoint'])
        if (not result['complete'] or selected['step'] != 4 or not result['fresh_optimizer']
                or result['starting_adapter_sha256'] != HISTORICAL_SHA
                or result['child_loaded'] or result['child_updated']
                or result['identity'] != read(PRIOR / 'READY.json')['identity']):
            raise ValueError('not the authenticated fixed-final4 interface SFT result')
        if read(result_path.parent / 'SELECTION.json') != selected:
            raise ValueError('SFT selection does not match its fixed final result')
        check(checkpoint / 'state.json', selected['state_sha256'])
        state = read(checkpoint / 'state.json')
        if (state['files_sha256'] != result['files_sha256'] or state['step'] != 4
                or state['identity'] != result['identity'] or state['epoch'] != 2 or state['cursor'] != 0):
            raise ValueError('SFT checkpoint state/cursor differs')
        expected = {'path': str(checkpoint), 'adapter_sha256': selected['adapter_sha256'],
                    'config_sha256': selected['config_sha256']}
        if model != expected:
            raise ValueError('selected model differs from final4')
        evidence = {str(checkpoint / k): h for k, h in result['files_sha256'].items()}
        evidence.update({str(result_path): value['result_sha256'],
                         str(result_path.parent / 'SELECTION.json'): value['selection_sha256'],
                         str(checkpoint / 'state.json'): selected['state_sha256']})
    else:
        raise ValueError('only the two explicitly named warm-start families are supported')
    if value['evidence_sha256'] != evidence:
        raise ValueError('starting lineage evidence closure differs')
    for path, expected in evidence.items():
        check(path, expected)
    for filename, key in [('adapter_model.safetensors', 'adapter_sha256'), ('adapter_config.json', 'config_sha256')]:
        check(Path(model['path']) / filename, model[key])
    return fresh_policy(model)


@functools.lru_cache(maxsize=1)
def verify_prepared():
    manifest = read(ROOT / 'CAMPAIGN.json')
    if digest({k: v for k, v in manifest.items() if k != 'campaign_id'}) != manifest['campaign_id']:
        raise ValueError('campaign identity changed')
    for path, expected in {**manifest['source_sha256'], **manifest['input_sha256']}.items():
        check(path, expected)
    if (ROOT / 'PREPARED.json').exists():
        ready = read(ROOT / 'PREPARED.json')
        check(ROOT / 'CAMPAIGN.json', ready['campaign_sha256'])
    return manifest
