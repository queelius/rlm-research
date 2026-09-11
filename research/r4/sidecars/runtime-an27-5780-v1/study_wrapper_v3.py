"""Accepted new runtime, driver, and actual launcher identity; scientific bytes pinned."""
import study_wrapper as base
import lifecycle_adapter

lifecycle_adapter.verify()
SOURCE = base.ROOT / 'study_wrapper.py'
if base.sha(SOURCE) != 'b7d1fcbb8788ebb10d4b1eb75f117c3b2e1d2cbbd9dc23ca94990eda521785f0':
    raise ValueError('CPU-qualified lifecycle wrapper changed')
source = SOURCE.read_text()
before = '        suite = base_dependencies()'
assert source.count(before) == 1
source = source.replace(before, before + '\n        lifecycle_adapter.install(suite)')
before = "result[1:2] = [str(ROOT / 'study_wrapper.py'), Path(result[1]).stem]"
assert source.count(before) == 1
source = source.replace(before, "result[1:2] = [str(ROOT / 'study_wrapper_v3.py'), Path(result[1]).stem]")
exec(compile(source, str(SOURCE) + ':service-driver-and-identity-v3', 'exec'), globals())
