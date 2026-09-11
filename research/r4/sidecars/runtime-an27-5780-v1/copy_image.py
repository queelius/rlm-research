"""Reuse exact bounded six-layer copier; replace only owned CPU affinity."""
import hashlib
from pathlib import Path
SOURCE = Path(__file__).resolve().parent.parent / 'runtime-local-cache-v1/copy_image.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '62b01f905ad7cc42e6a4fe40e73d2e8e5bf5259823fef7423842088bf7cf4cc8'
source = SOURCE.read_text()
assert source.count('os.sched_setaffinity(0,{34,35})') == 1
source = source.replace('os.sched_setaffinity(0,{34,35})', 'owned.check_owner();os.sched_setaffinity(0,owned.CPUS)')
exec(compile(source, str(SOURCE) + ':an27-lifecycle', 'exec'), globals())
