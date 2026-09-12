"""V2 unchanged checkpoint binding."""
import importlib.util,sys
from pathlib import Path
import study_v2 as study
ROOT=Path(__file__).resolve().parent;_old=sys.modules.get('study');sys.modules['study']=study
try:
    _spec=importlib.util.spec_from_file_location('mrcr_long_v1_checkpoint_for_v2',ROOT/'checkpoint.py')
    _module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module)
finally:
    if _old is None:sys.modules.pop('study',None)
    else:sys.modules['study']=_old
RECEIPT=_module.RECEIPT;verify_checkpoint=_module.verify_checkpoint;binding=_module.binding
