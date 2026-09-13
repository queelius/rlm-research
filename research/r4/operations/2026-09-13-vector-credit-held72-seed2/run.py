"""MAIN final sampling replication; fixed checkpoints and held contexts."""
from pathlib import Path
import types
source = Path(__file__).resolve().parent.parent / '2026-09-13-vector-credit-held72/run.py'
text = source.read_text()
for old, new in [
    ('b05-vector-credit-held72-eval-v3', 'b05-vector-credit-held72-seed2-v1'),
    ('56d8bdbe78dfeebac1db039978117f0c79b07418081477440acadd9082b01bca', '8ec6eaedbdba12ad0f55ae1ec06d896e6bad9e089181375d4ce1b91eb329dcaa'),
    ('Already frozen202609470000..23', 'Fresh frozen202609520000..23'),
]:
    assert text.count(old) == 1
    text = text.replace(old, new)
module = types.ModuleType('main_held72_seed2')
module.__file__ = __file__
exec(compile(text, str(source), 'exec'), module.__dict__)
if __name__ == '__main__':
    module.execute()
