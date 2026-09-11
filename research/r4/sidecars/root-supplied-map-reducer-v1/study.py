"""Pinned existing native runtime, new supplied-map task only."""
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'root-complete-demonstration-sft-v1'
RL4 = ROOT.parent / 'root-child-representation-bridge-rl4-v1'
NATIVE = Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def load(name, path, pin):
    if sha(path) != pin:
        raise ValueError('pinned source changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


@functools.lru_cache(maxsize=1)
def source():
    return load('supplied_complete_source', SOURCE / 'study.py',
                '26388b27fb97379145b87cfa60aeb7b93502e6880feb2e6a7ee33e652c70c1cb')


@functools.lru_cache(maxsize=1)
def stack():
    st = source().stack()
    st.prior.ROOT = ROOT
    return st


def binding():
    prior = load('supplied_rl4_binding_source', RL4 / 'study.py',
                 '381238761e1e8e6a8a906f6568942db39ec128c0f22732e6f02672bab567c711')
    result = prior.binding()
    for model in result['models'].values():
        if sha(Path(model['path']) / 'adapter_model.safetensors') != model['adapter_sha256']:
            raise ValueError('adapter bytes changed')
        if sha(Path(model['path']) / 'adapter_config.json') != model['config_sha256']:
            raise ValueError('adapter config changed')
    return result


def verify():
    from protocol import digest
    ready = read(ROOT / 'READY.json')
    if digest({k: v for k, v in ready.items() if k != 'identity'}) != ready['identity']:
        raise ValueError('READY identity')
    for path, expected in {**ready['source_sha256'], **ready['input_sha256']}.items():
        if sha(path) != expected:
            raise ValueError('READY closure changed: ' + path)
    return ready


def task(context, prompt, gold, row, labels=None):
    original = stack().native.task(context, prompt, gold, row['id'])
    helper = (ROOT / 'count_labels.py').read_bytes() if row.get('reducer') else None

    class SuppliedMapTask(type(original)):
        async def setup(self, trace, runtime):
            await super().setup(trace, runtime)
            if labels is not None:
                await runtime.write('labels.json', json.dumps(labels, sort_keys=True).encode())
            if helper is not None:
                await runtime.write('count_labels.py', helper)

    value = SuppliedMapTask(original.data, original.config)
    value.public_records = original.public_records
    value.plain_query = original.plain_query
    value.controller = 'free'
    return value


def interface(output):
    st = stack()
    with source().aliases({'interface': st.interface}):
        return st.local.configure_interface(output)
