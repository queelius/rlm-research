"""Fresh attempt after zero-model credential failure; only output/lifecycle paths adapt."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType
import credential_preflight
import lifecycle_adapter
import study_wrapper as runtime

ROOT = runtime.ROOT
SCIENCE = runtime.SCIENTIFIC
OLD_OUTPUT = 'outputs/attempt-001'
NEW_OUTPUT = 'outputs/attempt-002-an27-credential-recovery'
OUTPUT = SCIENCE / NEW_OUTPUT
WRAPPER = ROOT / 'recovery_wrapper.py'
COUNTS = {'study.py':1, 'binding.py':1, 'train.py':1, 'launch.py':2, 'capture.py':0, 'readout.py':0}

def transformed(filename):
    if runtime.sha(SCIENCE/'READY.json') != runtime.SCIENTIFIC_READY:
        raise ValueError('original scientific READY changed')
    original = SCIENCE / filename
    pins = json.loads((SCIENCE/'READY.json').read_text())['source_sha256']
    if runtime.sha(original) != pins[str(original)]:
        raise ValueError('original scientific source changed')
    source = original.read_text()
    if source.count(OLD_OUTPUT) != COUNTS[filename]:
        raise ValueError('counted attempt output seam changed: ' + filename)
    source = source.replace(OLD_OUTPUT, NEW_OUTPUT)
    if filename == 'launch.py':
        for entry in ('capture','train','readout'):
            before = "str(s.ROOT/'" + entry + ".py')"
            if source.count(before) != 1:
                raise ValueError('single scientific subprocess seam changed')
            source = source.replace(before, "str(RECOVERY_WRAPPER),'" + entry + "'")
    return source

def verify_recovery():
    credential_preflight.require_provider_credential()
    runtime.verify_runtime()
    lifecycle_adapter.verify()
    ready = json.loads((ROOT/'RECOVERY_READY.json').read_text())
    for path, digest in ready['source_and_evidence_sha256'].items():
        if runtime.sha(path) != digest:
            raise ValueError('accepted recovery source/evidence changed: '+path)
    for filename, digest in ready['transformed_source_sha256'].items():
        if hashlib.sha256(transformed(filename).encode()).hexdigest() != digest:
            raise ValueError('accepted path transformation changed')
    return ready

def install_science():
    sys.path.insert(0, str(SCIENCE))
    for filename in ('study.py','binding.py'):
        name = filename[:-3]
        module = ModuleType(name)
        module.__file__ = str(SCIENCE/filename)
        sys.modules[name] = module
        exec(compile(transformed(filename), str(SCIENCE/filename)+':fresh-recovery-output', 'exec'), module.__dict__)
    study = sys.modules['study']
    original_stack = study.stack
    study.stack = lambda: runtime.adapt_stack(original_stack())
    return study

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', choices=('verify','run','capture','train','readout'))
    args, rest = parser.parse_known_args()
    ready = verify_recovery()
    study = install_science()
    if args.command == 'verify':
        study.verify()
        print(json.dumps(dict(status='CPU_VERIFIED_FRESH_CREDENTIAL_RECOVERY', output=str(OUTPUT),
            recovery_ready_sha256=runtime.sha(ROOT/'RECOVERY_READY.json'), original_identity=study.verify()['identity'], gpu_calls=0)))
        return
    if args.command != 'run':
        filename = args.command+'.py'
        sys.argv = [str(SCIENCE/filename), *rest]
        scope = dict(__name__='__main__', __file__=str(SCIENCE/filename))
        exec(compile(transformed(filename), str(SCIENCE/filename)+':fresh-recovery-output', 'exec'), scope)
        return
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    options = p.parse_args(rest)
    if options.output.resolve() != OUTPUT or OUTPUT.exists():
        raise ValueError('only the unused explicit recovery attempt may launch')
    launch = ModuleType('complete_sft_credential_recovery_launch')
    launch.__file__ = str(SCIENCE/'launch.py')
    launch.RECOVERY_WRAPPER = WRAPPER
    exec(compile(transformed('launch.py'), str(SCIENCE/'launch.py')+':fresh-recovery-output', 'exec'), launch.__dict__)
    original_dependencies = launch.dependencies
    def dependencies():
        suite = original_dependencies()
        lifecycle_adapter.install(suite)
        study.write(OUTPUT/'RECOVERY_BINDING.json', dict(recovery_ready_sha256=runtime.sha(ROOT/'RECOVERY_READY.json'),
            original_scientific_ready_sha256=runtime.SCIENTIFIC_READY, old_failed_output=str(SCIENCE/OLD_OUTPUT),
            output=str(OUTPUT), fresh_after_zero_model_failure=True, resumed_optimizer=False))
        study.write(OUTPUT/'ALLOCATION_RUNTIME.json', runtime.delta(OUTPUT))
        return suite
    launch.dependencies = dependencies
    result = launch.execute(OUTPUT)
    print(result)
    raise SystemExit(0 if result['complete'] else 1)

if __name__ == '__main__':
    main()
