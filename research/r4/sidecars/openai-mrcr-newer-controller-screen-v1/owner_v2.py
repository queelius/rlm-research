"""Same owned services/caps; fresh attempt and repaired collector only."""
from pathlib import Path
import hashlib

path=Path(__file__).with_name('owner.py')
assert hashlib.sha256(path.read_bytes()).hexdigest()=='000c7e954c2f4ffd16f5838f64203ae44aafc46e99390b263501ff3f788a0287'
source=path.read_text()
for before,after,count in [('import study as s','import study_v2 as s',1),
    ("s.ROOT/'collect.py'","s.ROOT/'collect_v2.py'",1),
    ("s.ROOT/'READY.json'","s.ROOT/'READY_V2.json'",1),
    ('compare.report()','compare.report(s.ATTEMPT)',1)]:
    assert source.count(before)==count;source=source.replace(before,after)
exec(compile(source,str(path)+':cpu-validator-v2','exec'),globals())
