"""Private prior null/cost projection, explicitly implementer-owned."""
import hashlib
from pathlib import Path
import experiment as e
SOURCE=e.PRIOR/'results.py'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!='ab63a618f9cf6362f2241391f0218cb0497fef65e56b77cb29d8be70d030302a':raise ValueError('projection source changed')
text=SOURCE.read_text()
for before,after in [("('all16','filter16','free')","('all16','filter16')"),('INDEPENDENT_PROJECTION.json','IMPLEMENTER_PROJECTION.json'),('never48 independent observations','never32 independent observations')]:
    if text.count(before)!=1:raise ValueError('projection seam ambiguous')
    text=text.replace(before,after)
exec(compile(text,str(SOURCE)+':typed-operator-projection','exec'),globals())
