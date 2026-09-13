"""MAIN additive admission of directory-handshake repaired paired training."""
from pathlib import Path
import types

source = Path(__file__).resolve().parent.parent / '2026-09-13-paired-vector-credit/run.py'
text = source.read_text()
changes = [
    ('62f961601f164aec417bf636a2472f4caab17cde30c220451dfa7ad6581fcf64', 'ee4c84418327584da1397b34d45fe187c8908c449c61e91c9e6740cc4c644ec7'),
    ('a4ffa9de290941839ee75b19f2c0ae98fb69e845ad6a78ed79830b841562bfa1', 'f07077a70daeefacd7117780678563a8b253ba2ff74061c23f5efe0709c9af71'),
]
for before, after in changes:
    assert text.count(before) == 1
    text = text.replace(before, after)
assert text.count('-v2') == 2
text = text.replace('-v2', '-v3')
module = types.ModuleType('main_paired_credit_v3')
module.__file__ = __file__
exec(compile(text, str(source), 'exec'), module.__dict__)
if __name__ == '__main__':
    module.execute()
