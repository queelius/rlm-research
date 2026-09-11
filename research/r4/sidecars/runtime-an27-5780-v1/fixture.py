"""Reuse one qualified fake-provider native fixture, changing CPU/path lifecycle."""
import hashlib
from pathlib import Path
SOURCE = Path(__file__).resolve().parent.parent / 'runtime-local-cache-v1/fixture.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '9951c20fc2ddbf90a34babbe756567790258e404c80332cbbde10fad2b23400c'
source = SOURCE.read_text()
assert source.count("'os.sched_setaffinity(0, {34, 35})'") == 1
source = source.replace("'os.sched_setaffinity(0, {34, 35})'", "'os.sched_setaffinity(0, {14, 15})'")
exec(compile(source, str(SOURCE) + ':an27-lifecycle', 'exec'), globals())
