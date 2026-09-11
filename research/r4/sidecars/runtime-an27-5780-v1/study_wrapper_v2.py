"""CPU-qualified wrapper plus pinned, separately accepted service-driver seam."""
import json
from pathlib import Path
import study_wrapper as base

SOURCE = base.ROOT / 'study_wrapper.py'
SOURCE_SHA = 'b7d1fcbb8788ebb10d4b1eb75f117c3b2e1d2cbbd9dc23ca94990eda521785f0'
if base.sha(SOURCE) != SOURCE_SHA:
    raise ValueError('CPU-qualified lifecycle wrapper changed')
ready = json.loads((base.ROOT / 'LIFECYCLE_READY.json').read_text())
for path, digest in ready['source_sha256'].items():
    if base.sha(path) != digest:
        raise ValueError('accepted lifecycle source changed: ' + path)
if base.sha(base.ROOT / 'CPU_READY.json') != ready['cpu_ready_sha256']:
    raise ValueError('CPU readiness changed')
source = SOURCE.read_text()
before = '        suite = base_dependencies()'
assert source.count(before) == 1
source = source.replace(before, before + "\n        suite.SERVE = ROOT / 'service_wrapper.py'")
# Route scientific collector subprocesses through this accepted version as well.
before = "result[1:2] = [str(ROOT / 'study_wrapper.py'), Path(result[1]).stem]"
assert source.count(before) == 1
source = source.replace(before, "result[1:2] = [str(ROOT / 'study_wrapper_v2.py'), Path(result[1]).stem]")
exec(compile(source, str(SOURCE) + ':service-driver-v2', 'exec'), globals())
