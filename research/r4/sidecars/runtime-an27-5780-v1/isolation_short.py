"""Allocation5780 lifecycle-only binding around pinned qualified isolation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket

ROOT = Path(__file__).resolve().parent
OWNER = json.loads((ROOT / 'OWNER.json').read_text())
STORE = Path(OWNER['store'])
CPUS = set(OWNER['cpus'])
SOURCE = ROOT.parent / 'runtime-preinstalled-image-v1/isolation.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '39b05161903a7ee3aede406f9ab96ab80a3c03eff2cdb64828170dc5c12abf4c'
spec = importlib.util.spec_from_file_location('an27_pinned_isolation', SOURCE)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
original.ROOT, original.STORE, original.CPUSET = ROOT, STORE, ','.join(map(str, sorted(CPUS)))
original.CRUN = ROOT.parent / 'rootless-runtime-feasibility-v1/bin/crun-isolated'

def check_owner():
    if socket.gethostname() != OWNER['node'] or os.getuid() != OWNER['uid']:
        raise ValueError('allocation node/uid changed')
    if STORE.resolve() != STORE or STORE.stat().st_uid != os.getuid() or STORE.stat().st_mode & 0o077:
        raise ValueError('private store identity/owner/mode changed')
    if not CPUS.issubset(os.sched_getaffinity(0)):
        raise ValueError('runtime CPUs unavailable')

def command(arguments, inherited=None):
    check_owner()
    argv, env = original.command(arguments, inherited)
    assert argv.count('--signature-policy') == 1
    index = argv.index('--signature-policy')
    del argv[index:index + 2]
    return argv, env
