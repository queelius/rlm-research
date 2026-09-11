"""New join namespace over authenticated released-base service and native runtime."""
import contextlib
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
RUNTIME = SIDE / 'runtime-an27-5780-v1'
FREE = SIDE / 'leaf-free-id-correspondence-v1'
ATTEMPT = ROOT / 'outputs/attempt-001'
READY_PATH = ROOT / 'READY.json'
NATIVE = Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
IMAGE = '8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def read(path): return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        handle.write('\n')


def serialize(value): return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def load(name, path, pin):
    if sha(path) != pin: raise ValueError('immutable source changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def aliases(values):
    old = {k: sys.modules.get(k) for k in values}; sys.modules.update(values)
    try: yield
    finally:
        for k, v in old.items():
            if v is None: sys.modules.pop(k, None)
            else: sys.modules[k] = v


qualified = load('join_qualified_partition_base', SIDE / 'root-partition-final-interface-v1/study.py',
                 '374b8819e9ecfefaefe15169830b242b10ad99dcb8a40a34808c4ed088542079')
MODEL, service, lifecycle = qualified.MODEL, qualified.service, qualified.lifecycle


def validate_weights(): return qualified.validate_weights()
def tokenizer(): return qualified.tokenizer()


@functools.lru_cache(maxsize=1)
def role():
    return load('join_qualified_native_role', SIDE / 'leaf-role-routing-v1/source/routing.py',
                '8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f')


def verify():
    ready = read(READY_PATH)
    if digest({k: v for k, v in ready.items() if k != 'identity'}) != ready['identity']:
        raise ValueError('READY identity')
    for path, pin in ready['source_sha256'].items():
        if sha(path) != pin: raise ValueError('READY closure changed: ' + path)
    validate_weights()
    return ready

