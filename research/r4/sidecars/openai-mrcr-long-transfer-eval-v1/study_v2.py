"""Additive V2: bind the proven allocation dual-LoRA service dependency."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('mrcr_long_v1_study_for_v2',ROOT/'study.py')
_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module)
for _name in dir(_module):
    if not _name.startswith('_') and _name not in {'READY','dependencies'}:globals()[_name]=getattr(_module,_name)
READY=ROOT/'READY_V2.json'
def dependencies():
    """Use the eval facade that installs runtime-an22 at both startup boundaries."""
    return eval_study().dependencies()
