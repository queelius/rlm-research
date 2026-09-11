"""The adapter must not point writable operations at the live shared store."""
import importlib.util
from pathlib import Path


def adapter():
    path = Path(__file__).with_name('isolation.py')
    assert path.exists(), 'task-owned isolation adapter not yet implemented'
    spec = importlib.util.spec_from_file_location('tested_isolation', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_private_store_flags_and_environment_preserve_home():
    module = adapter()
    argv, env = module.command(['info'], {'HOME': '/original', 'PATH': '/usr/bin'})
    assert env['HOME'] == '/original'
    assert argv[argv.index('--root') + 1].startswith('/project/alex_phd/research-cache/runtime-images/')
    assert argv[argv.index('--runroot') + 1].startswith('/project/alex_phd/research-cache/runtime-images/')
    assert env['XDG_RUNTIME_DIR'].startswith('/project/alex_phd/research-cache/runtime-images/')
    assert not any('/tmp/rootless-runtime-feasibility-v1' in item for item in argv)


def test_runtime_run_adds_only_owned_workdir_and_cpu_limit():
    module = adapter()
    argv, _ = module.command(['run', '--workdir', '/app', 'sha256:example', 'sleep', 'infinity'], {})
    assert 'type=tmpfs,destination=/app' in argv
    assert argv[argv.index('--cpuset-cpus') + 1] == module.CPUSET
    assert argv.count('sha256:example') == 1
