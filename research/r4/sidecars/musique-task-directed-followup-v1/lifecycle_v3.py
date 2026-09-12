"""Exact V2 engine argv in the unchanged authenticated lifecycle claim function."""
import ast

import study_v3 as study

SOURCE = study.ROOT.parent / 'root-rlvr-campaign-v1/campaign_lifecycle_v2.py'
SOURCE_SHA = '568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5'


def install(suite):
    assert study.sha(SOURCE) == SOURCE_SHA
    original = SOURCE.read_text()
    node = next(n for n in ast.parse(original).body if isinstance(n, ast.FunctionDef) and n.name == 'claim_service')
    source = ast.get_source_segment(original, node)
    launcher = 'c.ROLE / "source/serve.py"'
    command = '[str(c.NATIVE_PYTHON.with_name("inference")), "@", str(service / "inference.json")]'
    assert source.count(launcher) == 2 and source.count(command) == 1
    source = source.replace(launcher, 'ALLOCATION_SERVICE').replace(command,
        '[str(c.NATIVE_PYTHON), str(REPORT_ENGINE_ENTRY), "@", str(service / "inference.json")]')
    suite.SERVE = study.ROOT / 'service_wrapper_v2.py'
    suite.life.ALLOCATION_SERVICE = suite.SERVE
    suite.life.REPORT_ENGINE_ENTRY = study.ROOT / 'engine_entry_v2.py'
    exec(compile(source, str(SOURCE) + ':report-exact-engine-v3', 'exec'), suite.life.__dict__)

