"""One unchanged native offline fixture with new owned cache/CPU paths."""
import hashlib
import importlib.util
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'runtime-preinstalled-image-v1/attempt-002'
p=OLD/'fixture3_adapter.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='0dc4eb2221b2746d46d5e8a20b58be496b683074956125ba0865daab2bcede12'
s=importlib.util.spec_from_file_location('local_pinned_fixture_adapter',p);adapter=importlib.util.module_from_spec(s);s.loader.exec_module(adapter)
source,edits=adapter.adapted_source()
before="SOURCE = ROOT.parents[1] / 'root-only-credit-v1/qualify_native.py'"
assert source.count(before)==1
source=source.replace(before,"SOURCE = ROOT.parent / 'root-only-credit-v1/qualify_native.py'")
assert source.count('os.sched_setaffinity(0, {32, 33})')==1
source=source.replace('os.sched_setaffinity(0, {32, 33})','os.sched_setaffinity(0, {34, 35})')
sys.path.append(str(OLD))
write_script=adapter.write_script
if __name__=='__main__':exec(compile(source,str(p)+':local-cache','exec'),globals())
