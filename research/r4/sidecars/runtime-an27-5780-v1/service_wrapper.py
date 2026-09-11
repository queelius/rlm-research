"""Pinned service with one explicit new-node driver-environment seam."""
import hashlib
import json
import os
from pathlib import Path
import sys
from types import ModuleType
import study_wrapper as runtime

SOURCE = runtime.ROOT.parent / 'leaf-role-routing-v1/source/serve.py'
SOURCE_SHA = '84c23753624bcbd5694c45f81e49712a78164500bf6fe63592217085a464a835'
DRIVER = '/export/software/system/nvidia/580.159.04/lib'

def adapt_environment(environment):
    value = dict(environment)
    libs = [p for p in value.get('LD_LIBRARY_PATH', '').split(':') if p and '580.126.09' not in p and p != DRIVER]
    value['LD_LIBRARY_PATH'] = ':'.join([DRIVER, *libs])
    value['PATH'] = value['PATH'].replace('/export/software/system/nvidia/580.126.09/bin', '/export/software/system/nvidia/580.159.04/bin')
    return value

def source_text():
    if runtime.sha(SOURCE) != SOURCE_SHA:
        raise ValueError('scientific service source changed')
    source = SOURCE.read_text()
    before = '    environment = helper._server_environment(helper._environment(), 0)'
    assert source.count(before) == 1
    after = before + '\n    environment = adapt_environment(environment)\n    write_once(args.run_dir / "ALLOCATION_DRIVER.json", {"source_sha256": "' + SOURCE_SHA + '", "wrapper_sha256": runtime_wrapper_sha, "driver_library_path": environment["LD_LIBRARY_PATH"], "old_driver_removed": True})'
    return source.replace(before, after)

def main():
    runtime.verify_runtime()
    if not Path(DRIVER).is_dir():
        raise ValueError('actual allocation driver missing')
    sys.path.insert(0, str(SOURCE.parent))
    module = ModuleType('allocation5780_pinned_service')
    module.__file__ = str(SOURCE)
    module.__dict__.update(adapt_environment=adapt_environment, runtime_wrapper_sha=runtime.sha(Path(__file__)))
    exec(compile(source_text(), str(SOURCE) + ':allocation-driver', 'exec'), module.__dict__)
    module.main()

if __name__ == '__main__':
    main()
