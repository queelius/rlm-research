"""Private local VFS rebinding; never opens the old store through Podman."""
import hashlib
import importlib.util
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STORE=Path('/tmp/rlmc.0m4242')
SOURCE=ROOT.parent/'runtime-preinstalled-image-v1/isolation.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='39b05161903a7ee3aede406f9ab96ab80a3c03eff2cdb64828170dc5c12abf4c'
spec=importlib.util.spec_from_file_location('local_original_isolation',SOURCE)
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
original.ROOT,original.STORE,original.CPUSET=ROOT,STORE,'34,35'
original.CRUN=ROOT.parent/'rootless-runtime-feasibility-v1/bin/crun-isolated'

def command(arguments,inherited=None):
    if STORE.resolve()!=STORE or STORE.stat().st_uid!=os.getuid():raise ValueError('private store identity changed')
    argv,env=original.command(arguments,inherited)
    assert argv.count('--signature-policy')==1
    i=argv.index('--signature-policy');del argv[i:i+2]
    return argv,env
