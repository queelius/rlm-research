"""MAIN selection-provenance binding repair; unchanged paired held72 experiment."""
from pathlib import Path
import types
source = Path(__file__).resolve().parent.parent / '2026-09-13-vector-credit-held72/run.py'
text = source.read_text()
assert text.count('b05-vector-credit-held72-eval-v3') == 1
text = text.replace('b05-vector-credit-held72-eval-v3', 'b05-vector-credit-held72-eval-v4')
before = '56d8bdbe78dfeebac1db039978117f0c79b07418081477440acadd9082b01bca'
assert text.count(before) == 1
text = text.replace(before, '94b1abf0ad9730d2b2df3b2dac50a9fe0a7e2fa5a7ff1187d04a328e3cf8999e')
module = types.ModuleType('main_held72_v4')
module.__file__ = __file__
exec(compile(text, str(source), 'exec'), module.__dict__)
if __name__ == '__main__':
    module.execute()
