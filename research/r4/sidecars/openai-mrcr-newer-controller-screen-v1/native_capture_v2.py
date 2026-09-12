"""Only hoist immutable tokenizer size out of the per-token validation loop."""
from pathlib import Path
import hashlib

path=Path(__file__).with_name('native_capture.py')
assert hashlib.sha256(path.read_bytes()).hexdigest()=='7d03e0ef3e638a336c70e318f57ce6bb1323b9799c226ffc4ef0439159d9787d'
source=path.read_text()
old='    assert all(type(i)is int and 0<=i<len(tokenizer) for i in ids+prompt)'
new='    vocab_size=len(tokenizer)\n    assert all(type(i)is int and 0<=i<vocab_size for i in ids+prompt)'
assert source.count(old)==1 and source.count('import study as s')==1
source=source.replace(old,new).replace('import study as s','import study_v2 as s')
exec(compile(source,str(path)+':hoisted-vocabulary-size','exec'),globals())
