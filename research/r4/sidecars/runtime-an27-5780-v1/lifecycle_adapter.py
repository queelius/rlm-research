"""Bind both launcher identity checks to the actual additive service wrapper."""
import ast
from pathlib import Path
import study_wrapper as runtime

SOURCE = runtime.ROOT.parent / 'root-rlvr-campaign-v1/campaign_lifecycle_v2.py'
SOURCE_SHA = '568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5'
SERVICE = runtime.ROOT / 'service_wrapper_v2.py'

def claim_source():
    if runtime.sha(SOURCE) != SOURCE_SHA:
        raise ValueError('pinned lifecycle source changed')
    source = SOURCE.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'claim_service')
    text = ast.get_source_segment(source, node)
    before = 'c.ROLE / "source/serve.py"'
    assert text.count(before) == 2
    return text.replace(before, 'ALLOCATION_SERVICE')

def verify():
    import json
    manifest = json.loads((runtime.ROOT / 'LIFECYCLE_READY_V2.json').read_text())
    for path, digest in manifest['source_sha256'].items():
        if runtime.sha(path) != digest:
            raise ValueError('accepted service lifecycle changed: ' + path)
    if runtime.sha(runtime.ROOT / 'CPU_READY.json') != manifest['cpu_ready_sha256']:
        raise ValueError('CPU readiness changed')

def install(suite):
    verify()
    suite.SERVE = SERVICE
    suite.life.__dict__['ALLOCATION_SERVICE'] = SERVICE
    exec(compile(claim_source(), str(SOURCE) + ':actual-wrapper-identity', 'exec'), suite.life.__dict__)
