"""Narrow private rootless Podman adapter; never reassigns HOME."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
STORE = Path('/project/alex_phd/research-cache/runtime-images/rpi-v1.WHYd2G')
STAGED = Path('/project/alex_phd/cache/rootless-runtime-feasibility-v1/rootfs')
CRUN = ROOT.parent / 'rootless-runtime-feasibility-v1/bin/crun-isolated'
CPUSET = '32,33'


def command(arguments, inherited=None):
    env = dict(os.environ if inherited is None else inherited)
    env.update(XDG_RUNTIME_DIR=str(STORE / 'runtime'),
               XDG_CONFIG_HOME=str(STORE / 'config'),
               CONTAINERS_CONF=str(ROOT / 'config/containers.conf'),
               CONTAINERS_REGISTRIES_CONF=str(ROOT / 'config/registries.conf'),
               LD_LIBRARY_PATH=str(STAGED / 'usr/lib/x86_64-linux-gnu'),
               PATH=str(STAGED / 'usr/bin') + ':/usr/bin:/bin',
               TMPDIR=str(STORE / 'tmp'))
    argv = [str(STAGED / 'usr/bin/podman'), '--root', str(STORE / 'root'),
            '--runroot', str(STORE / 'runroot'), '--storage-driver', 'vfs',
            '--storage-opt', 'vfs.ignore_chown_errors=true', '--runtime', str(CRUN),
            '--conmon', str(STAGED / 'usr/bin/conmon'), '--events-backend', 'file',
            '--cgroup-manager', 'cgroupfs', '--tmpdir', str(STORE / 'tmp'),
            '--signature-policy', str(ROOT / 'config/policy.json')]
    args = list(arguments)
    if args and args[0] == 'run':
        args[1:1] = ['--security-opt', 'no-new-privileges', '--cpuset-cpus', CPUSET]
        if '--workdir' in args and args[args.index('--workdir') + 1] == '/app':
            args[1:1] = ['--mount', 'type=tmpfs,destination=/app']
    if args and args[0] == 'rm':
        args[1:1] = ['--time', '0']
    return argv + args, env


def initialize():
    if STORE.resolve() != STORE or STORE.stat().st_uid != os.getuid():
        raise ValueError('private store identity/owner mismatch')
    for name in ['root', 'runroot', 'runtime', 'config', 'tmp']:
        (STORE / name).mkdir(mode=0o700, exist_ok=False)


def main():
    argv, env = command(sys.argv[1:])
    os.sched_setaffinity(0, {32, 33})
    os.execve(argv[0], argv, env)


if __name__ == '__main__':
    main()
