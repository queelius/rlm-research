"""Explicit parent/child lifecycle adaptation; pinned scientific sources unedited."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

import isolation_short as owned

ROOT = owned.ROOT
SCIENTIFIC = ROOT.parent / 'root-complete-demonstration-sft-v1'
IMAGE = '8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'
SCIENTIFIC_READY = 'c9fc31943e81f8b3597e134a5e26b6d9c162e868356d20a37765081fca4b5b23'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_runtime():
    owned.check_owner()
    ready = json.loads((ROOT / 'CPU_READY.json').read_text())
    if ready['private_store'] != str(owned.STORE) or ready['image_id'] != IMAGE or ready['cpu_affinity'] != [14,15]:
        raise ValueError('runtime readiness identity changed')
    for path, digest in ready['source_and_artifact_sha256'].items():
        if sha(path) != digest:
            raise ValueError('runtime source/proof changed: ' + path)
    if IMAGE not in {row['id'] for row in json.loads((owned.STORE / 'root/vfs-images/images.json').read_text())}:
        raise ValueError('qualified image absent')
    if sha(SCIENTIFIC / 'READY.json') != SCIENTIFIC_READY:
        raise ValueError('scientific READY changed')
    if '580.126.09' in os.environ.get('LD_LIBRARY_PATH', ''):
        raise ValueError('old driver library must not shadow allocation driver')
    return ready

def delta(output):
    return dict(schema='allocation5780-lifecycle-v1', original_scientific_ready_sha256=SCIENTIFIC_READY,
        runtime_ready_sha256=sha(ROOT / 'CPU_READY.json'), image_id=IMAGE,
        storage_root=str(owned.STORE), wrapper=str(ROOT / 'bin/docker'), wrapper_cpu_affinity=[14,15],
        verifiers_cache=str(owned.STORE / ('interface-cache-' + hashlib.sha256(str(output).encode()).hexdigest()[:20])),
        scientific_inputs_unchanged=True, gpu_model_qualification=False,
        driver_library_path=os.environ.get('LD_LIBRARY_PATH', ''))

def adapt_stack(st):
    local = st.local
    local.LOCAL, local.STORE = ROOT, owned.STORE
    def validate_store(path=None):
        owned.check_owner()
        if path is not None and Path(path) != owned.STORE:
            raise ValueError('nonowned runtime store')
        images = json.loads((owned.STORE / 'root/vfs-images/images.json').read_text())
        if IMAGE not in {row['id'] for row in images}:
            raise ValueError('qualified image absent')
    local.validate_store = validate_store
    local.delta = delta
    return st

def rewrite(argv):
    result = list(argv)
    if len(result) > 1 and result[1] in {str(SCIENTIFIC / 'capture.py'), str(SCIENTIFIC / 'readout.py')}:
        result[1:2] = [str(ROOT / 'study_wrapper.py'), Path(result[1]).stem]
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'run', 'capture', 'readout'))
    args, remaining = parser.parse_known_args()
    verify_runtime()
    sys.path.insert(0, str(SCIENTIFIC))
    import study as s
    base_stack = s.stack
    s.stack = lambda: adapt_stack(base_stack())
    if args.command == 'verify':
        if remaining:
            raise ValueError('unexpected verify arguments')
        s.verify()
        print(json.dumps(dict(status='CPU_VERIFIED', scientific_ready=SCIENTIFIC_READY,
            runtime_ready=sha(ROOT / 'CPU_READY.json'), gpu_calls=0)))
        return
    if args.command in ('capture', 'readout'):
        target = SCIENTIFIC / (args.command + '.py')
        sys.argv = [str(target), *remaining]
        runpy.run_path(str(target), run_name='__main__')
        return
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    opts = p.parse_args(remaining)
    import launch
    base_dependencies = launch.dependencies
    def dependencies():
        suite = base_dependencies()
        base_command = suite.command
        def command(directory, label, argv, cap, deadline):
            return base_command(directory, label, rewrite(argv), cap, deadline)
        suite.command = command
        s.write(opts.output / 'ALLOCATION_RUNTIME.json', delta(opts.output))
        return suite
    launch.dependencies = dependencies
    result = launch.execute(opts.output.resolve())
    print(result)
    raise SystemExit(0 if result['complete'] else 1)

if __name__ == '__main__':
    main()
