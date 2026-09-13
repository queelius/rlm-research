"""MAIN reuse of reviewed singleton admission for the fresh328-call replication."""
from pathlib import Path
import types

source = Path(__file__).resolve().parent.parent / '2026-09-13-singleton-decomposition/run.py'
text = source.read_text()
changes = [
    ("'b05-singleton-decomposition-v1'", "'b05-singleton-decomposition-replica-v1'"),
    ('06d962c024298d58cb87abefb54f03d2019fdbe5fd298cfd47c38edcbda2094c', 'df551ff0160dab37511a9e58406470885f1bedc47d36fba7c8668ca271a3d1eb'),
    ('planned_calls=176', 'planned_calls=328'),
    ('generation202609420000..5; roots202609430000..11', 'generation202609490000..11; roots202609500000..23'),
    ('All12 perarm', 'All24 perarm'),
    ('Six independent contexts', 'Twelve independent contexts'),
]
for before, after in changes:
    assert text.count(before) == 1, before
    text = text.replace(before, after)
module = types.ModuleType('main_singleton_replication')
module.__file__ = __file__
exec(compile(text, str(source), 'exec'), module.__dict__)

if __name__ == '__main__':
    module.execute()
