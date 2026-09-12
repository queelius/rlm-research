"""Fixed intermediate cp16 screen; prompts/seeds/caps inherit the accepted G4 study."""
import hashlib
from pathlib import Path
from types import ModuleType

ROOT=Path(__file__).resolve().parent
ORIGINAL=ROOT.parent/'openai-mrcr-procedural-sft32-onpolicy-screen-v1'
path=ORIGINAL/'study.py';raw=path.read_bytes()
if hashlib.sha256(raw).hexdigest()!='694badf1b8247749aab7128ef75df356cb55352ccd6d9caf76116941bc284c13':
    raise ValueError('inherited scientific study changed')
text=raw.decode()
for before,after in [('mrcr-procedural-sft-step32','mrcr-procedural-sft-step16'),
                     ('arm="procedural_sft32_onpolicy_screen"','arm="procedural_sft16_onpolicy_screen"')]:
    if text.count(before)!=1:raise ValueError('study transform boundary changed')
    text=text.replace(before,after)
_module=ModuleType('cp16_private_g4_study');_module.__file__=str(ROOT/'study.py')
exec(compile(text,str(path)+':fixed-cp16', 'exec'),_module.__dict__)
def __getattr__(name):return getattr(_module,name)

