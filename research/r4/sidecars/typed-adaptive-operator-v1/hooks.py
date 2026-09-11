"""One explicit setup-closure rebind of the qualified typed native hook."""
import hashlib
from pathlib import Path
import experiment as e

SOURCE=e.TYPED/'hooks.py'
SHA='dcdf82e6e8fe919fe3df105df9985d3ef67fb0d9868e0711ffa18e534a7281af'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SHA:raise ValueError('typed hook changed')
text=SOURCE.read_text();before='with e.capture.installed_hooks(binding,output):';after='with e.a.installed_hooks(binding,output):'
if text.count(before)!=1:raise ValueError('setup seam ambiguous')
ADAPTED=text.replace(before,after)
exec(compile(ADAPTED,str(SOURCE)+':adaptive-operator-setup','exec'),globals())
