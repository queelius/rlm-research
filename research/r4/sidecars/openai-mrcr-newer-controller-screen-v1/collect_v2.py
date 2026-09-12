"""Original collector, new validator, new READY identity; no policy/runtime changes."""
from pathlib import Path
import hashlib

path=Path(__file__).with_name('collect.py')
assert hashlib.sha256(path.read_bytes()).hexdigest()=='de6a343ee38d1fb292c58e0a016be6912b5be253aef74a4c473ab9357a668e86'
source=path.read_text()
for before,after,count in [('import study as s','import study_v2 as s',1),
    ('from native_capture import capture','from native_capture_v2 import capture',1),
    ("s.ROOT/'READY.json'","s.ROOT/'READY_V2.json'",1)]:
    assert source.count(before)==count;source=source.replace(before,after)
exec(compile(source,str(path)+':cpu-validator-v2','exec'),globals())
