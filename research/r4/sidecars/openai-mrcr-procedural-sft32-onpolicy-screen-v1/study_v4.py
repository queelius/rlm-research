"""Additive V4 receipt binding; scientific inputs remain V1-identical."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sft32_onpolicy_v3_study_for_v4',ROOT/'study_v3.py')
_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(_module)
for _name in dir(_module):
    if not _name.startswith('_') and _name!='READY':globals()[_name]=getattr(_module,_name)
READY=ROOT/'CPU_READY_V4.json'
